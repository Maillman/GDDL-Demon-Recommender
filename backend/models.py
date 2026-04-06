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
    level_id: str | None = None  # Single reference level (e.g. current page level) for similarity search
    desired_tags: dict[str, float] = {}  # tag name -> fraction (0.0–1.0)
    tier_min: float | None = None
    tier_max: float | None = None
    limit: int = 10
    show_beaten: bool = False  # If True, include already-beaten levels in results (never affects similarity search)
    # Server-populated from user_id; never set by the client
    user_beaten_ids: list[str] = []  # User's beaten levels; used for filtering and profile-mode similarity
    user_skills: dict[str, float] = {}  # User's skill distribution; used for profile-mode similarity


class RecommendedLevel(BaseModel):
    level: Level
    score: float
    reason: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendedLevel]
