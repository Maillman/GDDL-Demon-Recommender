"""FastAPI backend for the GDDL Demon Recommender."""

import asyncio
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
    if request.user_id:
        # Use the user's profile data for similarity only when no explicit inputs are provided
        use_user_profile = not request.level_id and not request.desired_tags
        try:
            if use_user_profile:
                user_beaten_ids, user_skills = await asyncio.gather(
                    gddl_client.fetch_user_beaten_level_ids(request.user_id),
                    gddl_client.fetch_user_skills(request.user_id),
                )
            else:
                user_beaten_ids = await gddl_client.fetch_user_beaten_level_ids(request.user_id)
                user_skills = {}
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch user data: {exc}")

        request = request.model_copy(update={
            "user_beaten_ids": user_beaten_ids,
            "user_skills": user_skills,
        })

    if not request.level_id and not request.desired_tags and not request.user_id:
        raise HTTPException(
            status_code=400,
            detail="Provide a level ID, desired tags, or user_id.",
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
