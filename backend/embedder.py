"""Generates embedding vectors for GDDL levels based on their tags and metadata."""

from functools import lru_cache
from sentence_transformers import SentenceTransformer
from models import Level

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load the embedding model once and cache it."""
    return SentenceTransformer(MODEL_NAME)


def level_to_text(level: Level) -> str:
    """Convert a level's metadata into a natural-language string for embedding.

    Tags are repeated proportionally to their ReactCount share so that
    dominant skillsets have greater influence on the embedding vector.
    A scale of 10 is used: a tag with 30% of votes appears 3 times,
    while every tag gets at least 1 occurrence.
    """
    if level.tags:
        words: list[str] = []
        for tag_name, weight in level.tags.items():
            words.extend([tag_name] * max(1, round(weight * 10)))
        tag_str = " ".join(words)
    else:
        tag_str = "unknown"
    return (
        f"{level.name} tier {level.tier} {level.difficulty} demon "
        f"skills: {tag_str}"
    )


def embed_levels(levels: list[Level]) -> list[list[float]]:
    """Return an embedding vector for each level in the list."""
    model = _get_model()
    texts = [level_to_text(lvl) for lvl in levels]
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_text(text: str) -> list[float]:
    """Embed an arbitrary text string (used for query vectors)."""
    model = _get_model()
    return model.encode([text], convert_to_numpy=True)[0].tolist()
