"""
sync.py — Pull all levels from the GDDL API and upsert them into ChromaDB.

Run manually or on a weekly schedule:
    python sync.py

Optional flags:
    --dry-run   Fetch and print level count without writing to the database.
"""

import asyncio
import argparse
from dotenv import load_dotenv

load_dotenv()

import gddl_client
import embedder
import db


TAGS_CONCURRENCY = 10  # Max simultaneous tag-fetch requests


async def _fetch_tags_for_levels(levels: list, semaphore: asyncio.Semaphore) -> None:
    """Fetch tags in-place for each level, respecting the semaphore."""
    async def _fetch_one(level) -> None:
        async with semaphore:
            level.tags = await gddl_client.fetch_level_tags(level.id)

    await asyncio.gather(*(_fetch_one(lvl) for lvl in levels))


async def run(dry_run: bool = False) -> None:
    print("Fetching levels from GDDL API...")
    levels = await gddl_client.fetch_all_levels()
    print(f"  Fetched {len(levels)} levels.")

    if dry_run:
        for lvl in levels[:5]:
            print(f"  Sample: {lvl.name!r} | tier={lvl.tier} | rating_count={lvl.rating_count}")
        print("Dry run — no data written.")
        return

    print("Loading cached rating counts from DB...")
    stored = db.get_stored_level_cache()

    needs_tags: list = []
    for lvl in levels:
        cached = stored.get(lvl.id)
        if cached is None:
            # New level — must fetch tags
            needs_tags.append(lvl)
        elif cached["rating_count"] != lvl.rating_count:
            # RatingCount changed — tags may have changed
            needs_tags.append(lvl)
        else:
            # Unchanged — restore cached tags
            lvl.tags = [t for t in cached["tags"].split(",") if t]

    print(f"  {len(needs_tags)} levels need tag refresh, {len(levels) - len(needs_tags)} use cached tags.")

    if needs_tags:
        print("Fetching tags for changed/new levels...")
        semaphore = asyncio.Semaphore(TAGS_CONCURRENCY)
        await _fetch_tags_for_levels(needs_tags, semaphore)
        print(f"  Done fetching tags.")

    print("Generating embeddings...")
    # Process in batches to avoid memory spikes
    batch_size = 128
    for i in range(0, len(levels), batch_size):
        batch = levels[i : i + batch_size]
        embeddings = embedder.embed_levels(batch)
        db.upsert_levels(batch, embeddings)
        print(f"  Upserted levels {i + 1}–{min(i + batch_size, len(levels))}")

    print(f"Sync complete. DB now contains {db.count()} levels.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync GDDL data to ChromaDB.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch only, do not write to DB.")
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run))
