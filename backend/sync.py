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


async def run(dry_run: bool = False) -> None:
    print("Fetching levels from GDDL API...")
    levels = await gddl_client.fetch_all_levels()
    print(f"  Fetched {len(levels)} levels.")

    if dry_run:
        for lvl in levels[:5]:
            print(f"  Sample: {lvl.name!r} | tier={lvl.tier} | tags={lvl.tags}")
        print("Dry run — no data written.")
        return

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
