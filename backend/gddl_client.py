"""Client for the GDDL (Geometry Dash Demon Ladder) API."""

import asyncio
import os
import httpx
from models import Level

BASE_URL = "https://gdladder.com/api"
PAGE_SIZE = 25  # Maximum allowed by the API
# Stay safely under the 100 req/min limit
_REQUEST_DELAY = 0.7  # seconds between paginated requests
_MAX_RETRIES = 5


def _get_headers() -> dict:
    api_key = os.getenv("GDDL_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}"} if api_key else {}


async def _get_with_retry(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    """GET with exponential backoff on 429 Too Many Requests."""
    for attempt in range(_MAX_RETRIES):
        response = await client.get(url, **kwargs)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        retry_after = response.headers.get("Retry-After")
        wait = float(retry_after) if retry_after else 2 ** attempt
        await asyncio.sleep(wait)
    # Final attempt — let raise_for_status surface the error
    response = await client.get(url, **kwargs)
    response.raise_for_status()
    return response


def _parse_level(raw: dict) -> Level:
    """Map a raw /api/level/search item to a Level model.

    Response shape (confirmed):
      {
        "ID": int,
        "Rating": float,      # community difficulty rating — used as tier
        "Enjoyment": float,
        "Meta": {
          "Name": str,
          "Difficulty": str,  # category label: Easy/Medium/Hard/Insane/Extreme/Official
          "Publisher": {"name": str} | null
        }
      }
    Tags are NOT included here; fetch them separately with fetch_level_tags().
    """
    meta = raw.get("Meta") or {}
    publisher = meta.get("Publisher") or {}
    return Level(
        id=str(raw.get("ID", "")),
        name=meta.get("Name", "Unknown"),
        tier=float(raw.get("Rating") or 0),
        difficulty=meta.get("Difficulty", "Unknown"),
        tags=[],
        enjoyment=raw.get("Enjoyment"),
        creator=publisher.get("name"),
        rating_count=raw.get("RatingCount"),
    )


async def fetch_all_levels() -> list[Level]:
    """Fetch every level on the GDDL via paginated /api/level/search (max 25/page)."""
    levels: list[Level] = []
    page = 0
    async with httpx.AsyncClient(headers=_get_headers(), timeout=30.0) as client:
        while True:
            if page > 0:
                await asyncio.sleep(_REQUEST_DELAY)
            response = await _get_with_retry(
                client,
                f"{BASE_URL}/level/search",
                params={"limit": PAGE_SIZE, "page": page, "sort": "ID", "sortDirection": "asc"},
            )
            data = response.json()
            items: list[dict] = data.get("levels", [])
            if not items:
                break
            levels.extend(_parse_level(item) for item in items)
            if len(levels) >= data.get("total", 0):
                break
            page += 1
    return levels


async def fetch_level(level_id: str) -> Level:
    """Fetch a single level by its Level ID."""
    async with httpx.AsyncClient(headers=_get_headers(), timeout=10.0) as client:
        response = await _get_with_retry(client, f"{BASE_URL}/level/{level_id}")
        return _parse_level(response.json())


async def fetch_level_tags(level_id: str) -> list[str]:
    """Fetch tag names for a level from /api/level/{ID}/tags.

    Returns tag names sorted by community vote count (ReactCount) descending,
    so the most-voted skillset appears first.
    """
    async with httpx.AsyncClient(headers=_get_headers(), timeout=10.0) as client:
        response = await _get_with_retry(client, f"{BASE_URL}/level/{level_id}/tags")
        items: list[dict] = response.json()
        items.sort(key=lambda x: x.get("ReactCount", 0), reverse=True)
        return [item["Tag"]["Name"] for item in items if item.get("Tag")]
