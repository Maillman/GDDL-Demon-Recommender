"""
sync.py — Pull all levels from the GDDL API and upsert them into ChromaDB.

Run manually or on a weekly schedule:
    python sync.py

Optional flags:
    --dry-run   Fetch and print level count without writing to the database.

Resumable sync
--------------
A checkpoint file (sync_checkpoint.json) is written after every batch of tag
fetches.  If the script is interrupted (Ctrl-C or crash), re-running it will
resume from where it left off — the level list will NOT be re-fetched and any
tags already retrieved will be reused.  The checkpoint is deleted automatically
on a successful full sync.

The checkpoint path can be overridden with the SYNC_CHECKPOINT_FILE env var.
"""

import asyncio
import argparse
import json
import os
from dotenv import load_dotenv

load_dotenv()

import gddl_client
import embedder
import db
from models import Level


TAGS_CONCURRENCY = 1       # Max simultaneous tag-fetch requests
CHECKPOINT_SAVE_INTERVAL = 50  # Save checkpoint after every N tag fetches
CHECKPOINT_FILE = os.getenv("SYNC_CHECKPOINT_FILE", "sync_checkpoint.json")


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint() -> dict | None:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
        # Detect old checkpoint format where tags_fetched stored lists instead of dicts.
        tags = data.get("tags_fetched", {})
        if tags and isinstance(next(iter(tags.values())), list):
            print("  Old checkpoint format detected (tags as list); discarding and starting fresh.")
            return None
        return data
    return None


def _save_checkpoint(levels: list[Level], tags_fetched: dict[str, dict[str, float]]) -> None:
    """Write checkpoint atomically so a crash mid-write can't corrupt it."""
    tmp = CHECKPOINT_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(
            {
                "levels": [lvl.model_dump() for lvl in levels],
                "tags_fetched": tags_fetched,
            },
            f,
        )
    os.replace(tmp, CHECKPOINT_FILE)


def _clear_checkpoint() -> None:
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print(f"  Checkpoint cleared: {CHECKPOINT_FILE}")


# ---------------------------------------------------------------------------
# Tag fetching with batched progress saves
# ---------------------------------------------------------------------------

async def _fetch_tags_with_progress(
    needs_tags: list[Level],
    tags_fetched: dict[str, dict[str, float]],
    all_levels: list[Level],
    semaphore: asyncio.Semaphore,
) -> None:
    """Fetch tags in batches, saving a checkpoint after each batch.

    On CancelledError (Ctrl-C), any completed fetches in the interrupted batch
    are saved before re-raising so progress is not lost.
    """
    total = len(needs_tags)
    completed = 0

    async def _fetch_one(level: Level) -> None:
        async with semaphore:
            try:
                level.tags = await gddl_client.fetch_level_tags(level.id)
            except Exception as exc:
                print(f"  Warning: failed to fetch tags for {level.id} ({exc})")

    for i in range(0, total, CHECKPOINT_SAVE_INTERVAL):
        batch = needs_tags[i : i + CHECKPOINT_SAVE_INTERVAL]
        interrupted = False
        try:
            await asyncio.gather(*(_fetch_one(lvl) for lvl in batch))
        except asyncio.CancelledError:
            interrupted = True

        # Record whatever tags were set (even if the batch was only partially done)
        for lvl in batch:
            if lvl.tags:
                tags_fetched[lvl.id] = lvl.tags

        completed = min(i + CHECKPOINT_SAVE_INTERVAL, total)
        _save_checkpoint(all_levels, tags_fetched)
        print(f"  Tags fetched: {completed}/{total}")

        if interrupted:
            print(f"\nInterrupted. Progress saved to checkpoint — re-run to continue.")
            raise asyncio.CancelledError


# ---------------------------------------------------------------------------
# Main sync
# ---------------------------------------------------------------------------

async def run(dry_run: bool = False) -> None:
    # --- Step 1: get levels (from checkpoint or API) -----------------------
    checkpoint = _load_checkpoint()
    if checkpoint:
        print(f"Resuming from checkpoint: {CHECKPOINT_FILE}")
        levels = [Level(**lvl) for lvl in checkpoint["levels"]]
        tags_fetched: dict[str, dict[str, float]] = checkpoint.get("tags_fetched", {})
        print(f"  Loaded {len(levels)} levels, {len(tags_fetched)} already have tags.")
    else:
        print("Fetching levels from GDDL API...")
        levels = await gddl_client.fetch_all_levels()
        print(f"  Fetched {len(levels)} levels.")
        tags_fetched = {}
        _save_checkpoint(levels, tags_fetched)
        print(f"  Level list saved to checkpoint: {CHECKPOINT_FILE}")

    if dry_run:
        for lvl in levels[:5]:
            print(f"  Sample: {lvl.name!r} | tier={lvl.tier} | rating_count={lvl.rating_count}")
        print("Dry run — no data written.")
        return

    # --- Step 2: decide which levels need a tag refresh --------------------
    print("Loading cached rating counts from DB...")
    stored = db.get_stored_level_cache()

    needs_tags: list[Level] = []
    for lvl in levels:
        if lvl.id in tags_fetched:
            # Already fetched in this run (from checkpoint)
            lvl.tags = tags_fetched[lvl.id]
        else:
            cached = stored.get(lvl.id)
            if cached is None or cached["rating_count"] != lvl.rating_count:
                needs_tags.append(lvl)
            else:
                lvl.tags = json.loads(cached["tags"]) if cached.get("tags") else {}

    already_done = len(levels) - len(needs_tags)
    print(f"  {len(needs_tags)} levels need tag fetch, {already_done} use cached/checkpoint tags.")

    # --- Step 3: fetch tags for changed/new levels -------------------------
    if needs_tags:
        print("Fetching tags for changed/new levels...")
        semaphore = asyncio.Semaphore(TAGS_CONCURRENCY)
        await _fetch_tags_with_progress(needs_tags, tags_fetched, levels, semaphore)
        print("  Done fetching tags.")

    # --- Step 4: embed and upsert ------------------------------------------
    print("Generating embeddings and upserting to DB...")
    batch_size = 128
    for i in range(0, len(levels), batch_size):
        batch = levels[i : i + batch_size]
        embeddings = embedder.embed_levels(batch)
        db.upsert_levels(batch, embeddings)
        print(f"  Upserted levels {i + 1}–{min(i + batch_size, len(levels))}")

    _clear_checkpoint()
    print(f"Sync complete. DB now contains {db.count()} levels.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync GDDL data to ChromaDB.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch only, do not write to DB.")
    args = parser.parse_args()
    try:
        asyncio.run(run(dry_run=args.dry_run))
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
