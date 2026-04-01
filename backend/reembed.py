"""
reembed.py — Recompute embeddings for every level already in ChromaDB.

Use this after changing level_to_text() in embedder.py to update all stored
vectors without re-fetching any data from the GDDL API.

    python reembed.py

Optional flags:
    --batch-size N   Number of levels to embed per batch (default: 128).
    --dry-run        Print sample texts without writing to the DB.
"""

import argparse
import json

from models import Level
import db
import embedder


def _load_all_levels() -> list[Level]:
    """Reconstruct Level objects from everything stored in ChromaDB."""
    collection = db.get_collection()
    result = collection.get(include=["metadatas"])
    levels: list[Level] = []
    for level_id, meta in zip(result["ids"], result["metadatas"]):
        levels.append(Level(
            id=level_id,
            name=meta.get("name", ""),
            tier=float(meta.get("tier", 0)),
            difficulty=meta.get("difficulty", "Unknown"),
            tags=json.loads(meta.get("tags", "{}")),
            enjoyment=meta.get("enjoyment") if meta.get("enjoyment", -1.0) >= 0 else None,
            creator=meta.get("creator") or None,
            rating_count=meta.get("rating_count") if meta.get("rating_count", -1) >= 0 else None,
        ))
    return levels


def run(batch_size: int = 128, dry_run: bool = False) -> None:
    print("Loading levels from ChromaDB...")
    levels = _load_all_levels()
    print(f"  Found {len(levels)} levels.")

    if dry_run:
        for lvl in levels[:5]:
            print(f"  {lvl.name!r}: {embedder.level_to_text(lvl)!r}")
        print("Dry run — no embeddings written.")
        return

    print(f"Re-embedding in batches of {batch_size}...")
    for i in range(0, len(levels), batch_size):
        batch = levels[i : i + batch_size]
        embeddings = embedder.embed_levels(batch)
        db.upsert_levels(batch, embeddings)
        print(f"  Re-embedded levels {i + 1}–{min(i + batch_size, len(levels))}")

    print(f"Done. {len(levels)} levels updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recompute ChromaDB embeddings from stored metadata.")
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(batch_size=args.batch_size, dry_run=args.dry_run)
