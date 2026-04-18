"""FastAPI backend for the GDDL Demon Recommender."""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import db
import recommender
from models import RecommendRequest, RecommendResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the ChromaDB client on startup
    db.get_collection()
    yield


app = FastAPI(
    title="GDDL Demon Recommender API",
    version="1.0.3",
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
    if not request.level_id and not request.desired_tags and not request.user_beaten_ids:
        raise HTTPException(
            status_code=400,
            detail="Provide a level ID, desired tags, or user beaten IDs.",
        )
    results = recommender.recommend(request)
    return RecommendResponse(recommendations=results)
