from pydantic import BaseModel


class Level(BaseModel):
    id: str
    name: str
    tier: float
    difficulty: str
    tags: dict[str, float] = {}  # tag name -> fraction of total ReactCount (0.0–1.0)
    enjoyment: float | None = None
    creator: str | None = None
    rating_count: int | None = None


class RecommendRequest(BaseModel):
    user_id: int | None = None  # GDDL user ID; if provided, beaten levels + skills are fetched automatically
    beaten_level_ids: list[str] = []
    desired_tags: dict[str, float] = {}  # tag name -> fraction (0.0–1.0)
    tier_min: float | None = None
    tier_max: float | None = None
    limit: int = 10


class RecommendedLevel(BaseModel):
    level: Level
    score: float
    reason: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedLevel]
