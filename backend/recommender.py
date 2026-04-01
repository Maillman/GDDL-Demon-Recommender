"""Core recommendation logic."""

import json
import numpy as np
from embedder import embed_text
from models import Level, RecommendedLevel, RecommendRequest
import db


def _metadata_to_level(level_id: str, meta: dict) -> Level:
    return Level(
        id=level_id,
        name=meta["name"],
        tier=float(meta["tier"]),
        difficulty=meta["difficulty"],
        tags=json.loads(meta.get("tags", "{}")),
        enjoyment=meta.get("enjoyment") if meta.get("enjoyment", -1.0) >= 0 else None,
        creator=meta.get("creator") or None,
    )


def _build_query_vector(
    request: RecommendRequest,
) -> list[float]:
    """Combine beaten-level embeddings and desired-tag text into one query vector."""
    vecs: list[list[float]] = []

    # Average the embeddings of all beaten levels
    if request.beaten_level_ids:
        result = db.get_by_ids(request.beaten_level_ids)
        embeddings = result.get("embeddings", [])
        vecs.extend(embeddings)

    # Embed the desired-tag string if provided, repeating tags proportionally
    if request.desired_tags:
        words: list[str] = []
        for tag_name, weight in request.desired_tags.items():
            words.extend([tag_name] * max(1, round(weight * 10)))
        vecs.append(embed_text(" ".join(words)))

    # Fall back to a generic query if nothing was provided
    if not vecs:
        vecs.append(embed_text("demon level"))

    avg = np.mean(vecs, axis=0).tolist()
    return avg


def _tier_filter(request: RecommendRequest) -> dict | None:
    """Build a ChromaDB `where` clause for tier filtering."""
    if request.tier_min is None and request.tier_max is None:
        return None
    conditions = []
    if request.tier_min is not None:
        conditions.append({"tier": {"$gte": request.tier_min}})
    if request.tier_max is not None:
        conditions.append({"tier": {"$lte": request.tier_max}})
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _make_reason(level: Level, request: RecommendRequest) -> str:
    matching_tags = [t for t in level.tags if t in request.desired_tags]
    if matching_tags:
        return f"Matches desired skills: {', '.join(matching_tags)}. Tier {level.tier}."
    return f"Similar skillset to your beaten levels. Tier {level.tier}."


def recommend(request: RecommendRequest) -> list[RecommendedLevel]:
    if db.count() == 0:
        return []

    query_vec = _build_query_vector(request)
    where = _tier_filter(request)

    results = db.query(
        query_embedding=query_vec,
        n_results=request.limit,
        where=where,
    )

    recommendations: list[RecommendedLevel] = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    beaten_set = set(request.beaten_level_ids)

    for level_id, meta, dist in zip(ids, metadatas, distances):
        if level_id in beaten_set:
            continue
        level = _metadata_to_level(level_id, meta)
        # Cosine distance → similarity score (0–1, higher is better)
        score = round(1.0 - dist, 4)
        recommendations.append(
            RecommendedLevel(
                level=level,
                score=score,
                reason=_make_reason(level, request),
            )
        )

    return recommendations
