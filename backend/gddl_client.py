"""Client for the GDDL (Geometry Dash Demon Ladder) API."""

import os
import httpx
from models import Level

BASE_URL = "https://gdladder.com/api"


def _get_headers() -> dict:
    api_key = os.getenv("GDDL_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}"} if api_key else {}


def _parse_level(raw: dict) -> Level:
    """Map a raw GDDL API response dict to a Level model.

    NOTE: Field names here are placeholders until the actual GDDL API
    response shape is confirmed in Phase 1 of the project.
    """
    tags: list[str] = raw.get("tags") or raw.get("skillsets") or []
    return Level(
        id=str(raw.get("id") or raw.get("levelID", "")),
        name=raw.get("name") or raw.get("levelName", "Unknown"),
        tier=int(raw.get("tier", 0)),
        difficulty=raw.get("difficulty") or raw.get("difficultyName", "Demon"),
        tags=tags,
        enjoyment=raw.get("enjoyment"),
        creator=raw.get("creator") or raw.get("creatorName"),
    )


async def fetch_all_levels() -> list[Level]:
    """Fetch every level currently on the GDDL."""
    async with httpx.AsyncClient(headers=_get_headers(), timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/demons")
        response.raise_for_status()
        data = response.json()
        # The API may return the list directly or wrapped in a key — handle both.
        items: list[dict] = data if isinstance(data, list) else data.get("demons", data.get("data", []))
        return [_parse_level(item) for item in items]


async def fetch_level(level_id: str) -> Level:
    """Fetch a single level by its GDDL ID."""
    async with httpx.AsyncClient(headers=_get_headers(), timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}/demons/{level_id}")
        response.raise_for_status()
        return _parse_level(response.json())
