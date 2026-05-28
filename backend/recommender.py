"""Core recommendation logic."""

import json
import numpy as np
from embedder import embed_text
from models import Level, RecommendedLevel, RecommendRequest
import db


def _metadata_to_level(level_id: str, meta: dict) -> Level:
    raw_rc = meta.get("rating_count", -1)
    return Level(
        id=level_id,
        name=meta["name"],
        tier=float(meta["tier"]),
        difficulty=meta["difficulty"],
        tags=json.loads(meta.get("tags", "{}")),
        enjoyment=meta.get("enjoyment") if meta.get("enjoyment", -1.0) >= 0 else None,
        creator=meta.get("creator") or None,
        rating_count=int(raw_rc) if raw_rc is not None and raw_rc >= 0 else None,
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


def _metadata_filter(request: RecommendRequest) -> dict | None:
    """Build a ChromaDB `where` clause for numeric metadata filters."""
    conditions = []
    if request.tier_min is not None:
        conditions.append({"tier": {"$gte": request.tier_min}})
    if request.tier_max is not None:
        conditions.append({"tier": {"$lte": request.tier_max}})
    # enjoyment is stored as -1.0 when absent; $gte with a real value naturally excludes those
    if request.enjoyment_min is not None:
        conditions.append({"enjoyment": {"$gte": request.enjoyment_min}})
    if request.enjoyment_max is not None:
        conditions.append({"enjoyment": {"$lte": request.enjoyment_max}})
    if request.rating_count_min is not None:
        conditions.append({"rating_count": {"$gte": request.rating_count_min}})
    if request.rating_count_max is not None:
        conditions.append({"rating_count": {"$lte": request.rating_count_max}})
    if not conditions:
        return None
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
    where = _metadata_filter(request)

    ignore_set = set(request.user_beaten_ids) if not request.show_beaten else set()
    if request.level_id:
        ignore_set.add(request.level_id)

    creator_filter = request.creator.strip() if request.creator else None

    if creator_filter:
        return _recommend_with_creator_filter(request, query_vec, where, ignore_set, creator_filter)

    n_results = min(request.limit + len(ignore_set), db.count())
    results = db.query(query_embedding=query_vec, n_results=n_results, where=where)

    recommendations: list[RecommendedLevel] = []
    ids = results.get("ids", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for level_id, meta, dist in zip(ids, metadatas, distances):
        if level_id in ignore_set:
            continue
        if len(recommendations) >= request.limit:
            break
        level = _metadata_to_level(level_id, meta)
        score = round(1.0 - dist, 4)
        recommendations.append(
            RecommendedLevel(level=level, score=score, reason=_make_reason(level, request))
        )

    return recommendations


def _recommend_with_creator_filter(
    request: RecommendRequest,
    query_vec: list[float],
    where: dict | None,
    ignore_set: set[str],
    creator_filter: str,
) -> list[RecommendedLevel]:
    """Creator filtering requires substring matching, which ChromaDB's HNSW can't do.
    Fetch all matching docs and rank with numpy cosine similarity instead."""
    all_docs = db.get_all(where=where)
    ids = all_docs.get("ids", [])
    metadatas = all_docs.get("metadatas", [])
    embeddings = all_docs.get("embeddings", [])

    if not ids:
        return []

    q = np.array(query_vec)
    q_norm = np.linalg.norm(q)

    candidates: list[tuple[float, str, dict]] = []
    for level_id, meta, emb in zip(ids, metadatas, embeddings):
        if level_id in ignore_set:
            continue
        if creator_filter not in (meta.get("creator") or ""):
            continue
        e = np.array(emb)
        denom = q_norm * np.linalg.norm(e)
        similarity = float(np.dot(q, e) / denom) if denom > 0 else 0.0
        candidates.append((similarity, level_id, meta))

    candidates.sort(key=lambda x: x[0], reverse=True)

    recommendations: list[RecommendedLevel] = []
    for similarity, level_id, meta in candidates:
        if len(recommendations) >= request.limit:
            break
        level = _metadata_to_level(level_id, meta)
        recommendations.append(
            RecommendedLevel(
                level=level,
                score=round(similarity, 4),
                reason=_make_reason(level, request),
            )
        )

    return recommendations
