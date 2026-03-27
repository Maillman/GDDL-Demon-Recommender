from pydantic import BaseModel


class Level(BaseModel):
    id: str
    name: str
    tier: int
    difficulty: str
    tags: list[str]
    enjoyment: float | None = None
    creator: str | None = None


class RecommendRequest(BaseModel):
    beaten_level_ids: list[str] = []
    desired_tags: list[str] = []
    tier_min: int | None = None
    tier_max: int | None = None
    limit: int = 10


class RecommendedLevel(BaseModel):
    level: Level
    score: float
    reason: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedLevel]
