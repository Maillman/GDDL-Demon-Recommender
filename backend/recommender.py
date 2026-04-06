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
    """Combine reference-level embedding and/or desired-tag text into one query vector.

    Explicit mode (level_id or desired_tags provided): use only those inputs.
    Profile mode (neither provided): use the user's beaten levels + skill distribution.
    """
    vecs: list[list[float]] = []

    if request.level_id or request.desired_tags:
        # Explicit mode: embed the single reference level
        if request.level_id:
            result = db.get_by_ids([request.level_id])
            vecs.extend(result.get("embeddings", []))

        # Embed desired-tag text, repeating tags proportionally to weight
        if request.desired_tags:
            words: list[str] = []
            for tag_name, weight in request.desired_tags.items():
                words.extend([tag_name] * max(1, round(weight * 20)))
            vecs.append(embed_text(" ".join(words)))
    else:
        # Profile mode: average embeddings of the user's beaten levels
        if request.user_beaten_ids:
            result = db.get_by_ids(request.user_beaten_ids)
            vecs.extend(result.get("embeddings", []))

        # Include the user's skill distribution
        if request.user_skills:
            words = []
            for tag_name, weight in request.user_skills.items():
                words.extend([tag_name] * max(1, round(weight * 20)))
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


def _make_reason(level: Level, request: RecommendRequest, max_tags: int = 3) -> str:
    top_tags = list(level.tags)[:max_tags]
    query_tags = request.desired_tags or request.user_skills
    matching_tags = [t for t in top_tags if t in query_tags]
    if matching_tags:
        return f"Matches desired skills: {', '.join(matching_tags)}."
    if request.level_id:
        return f"Similar to this level."
    return f"Similar skillset to your profile."


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

    beaten_set = set(request.user_beaten_ids) if not request.show_beaten else set()

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
