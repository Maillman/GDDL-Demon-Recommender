from pydantic import BaseModel


class Level(BaseModel):
    id: str
    name: str
    tier: float
    difficulty: str
    tags: list[str]
    enjoyment: float | None = None
    creator: str | None = None
    rating_count: int | None = None


class RecommendRequest(BaseModel):
    beaten_level_ids: list[str] = []
    desired_tags: list[str] = []
    tier_min: float | None = None
    tier_max: float | None = None
    limit: int = 10


class RecommendedLevel(BaseModel):
    level: Level
    score: float
    reason: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedLevel]
