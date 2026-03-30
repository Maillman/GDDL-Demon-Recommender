"""ChromaDB setup and helpers."""

import os
from functools import lru_cache
import chromadb
from chromadb.config import Settings
from models import Level

COLLECTION_NAME = "gddl_levels"
DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")


@lru_cache(maxsize=1)
def get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection() -> chromadb.Collection:
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_levels(levels: list[Level], embeddings: list[list[float]]) -> None:
    """Insert or update levels in the ChromaDB collection."""
    collection = get_collection()
    collection.upsert(
        ids=[lvl.id for lvl in levels],
        embeddings=embeddings,
        metadatas=[
            {
                "name": lvl.name,
                "tier": lvl.tier,
                "difficulty": lvl.difficulty,
                "tags": ",".join(lvl.tags),
                "enjoyment": lvl.enjoyment if lvl.enjoyment is not None else -1.0,
                "creator": lvl.creator or "",
                "rating_count": lvl.rating_count if lvl.rating_count is not None else -1,
            }
            for lvl in levels
        ],
        documents=[lvl.name for lvl in levels],
    )


def query(
    query_embedding: list[float],
    n_results: int = 10,
    where: dict | None = None,
) -> chromadb.QueryResult:
    collection = get_collection()
    kwargs: dict = {"query_embeddings": [query_embedding], "n_results": n_results}
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)


def get_by_ids(level_ids: list[str]) -> chromadb.GetResult:
    collection = get_collection()
    return collection.get(ids=level_ids, include=["embeddings", "metadatas"])


def get_stored_level_cache() -> dict[str, dict]:
    """Return a mapping of level_id -> {rating_count, tags} for all stored levels.

    Used by sync.py to decide which levels need a tag refresh.
    """
    collection = get_collection()
    result = collection.get(include=["metadatas"])
    cache: dict[str, dict] = {}
    for level_id, meta in zip(result["ids"], result["metadatas"]):
        cache[level_id] = {
            "rating_count": meta.get("rating_count", -1),
            "tags": meta.get("tags", ""),
        }
    return cache


def count() -> int:
    return get_collection().count()
