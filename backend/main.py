"""FastAPI backend for the GDDL Demon Recommender."""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import db
import recommender
from models import RecommendRequest, RecommendResponse, Level
import gddl_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the ChromaDB client on startup
    db.get_collection()
    yield


app = FastAPI(
    title="GDDL Demon Recommender API",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the Chrome extension and local dev to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "level_count": db.count()}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest) -> RecommendResponse:
    if not request.beaten_level_ids and not request.desired_tags:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one beaten level ID or desired tag.",
        )
    results = recommender.recommend(request)
    return RecommendResponse(recommendations=results)


@app.get("/levels/{level_id}", response_model=Level)
async def get_level(level_id: str) -> Level:
    """Proxy a single level lookup to the GDDL API."""
    try:
        return await gddl_client.fetch_level(level_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
