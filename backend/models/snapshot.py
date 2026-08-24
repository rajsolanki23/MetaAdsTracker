from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DailySnapshotBase(BaseModel):
    creative_id: str = Field(..., description="Foreign key to Creative")
    client_id: str = Field(..., description="Foreign key to Client")
    date: str = Field(..., description="Calendar date YYYY-MM-DD (immutable key)")
    spend: float = Field(0.0, ge=0.0, description="Spend in client currency")
    revenue: float = Field(0.0, ge=0.0, description="Purchase conversion value / revenue")
    purchases: int = Field(0, ge=0, description="Number of purchase conversions")
    impressions: int = Field(0, ge=0, description="Ad impressions")
    clicks: int = Field(0, ge=0, description="Link clicks")
    roas: float = Field(0.0, ge=0.0, description="Return On Ad Spend (revenue / spend)")
    ctr: float = Field(0.0, ge=0.0, description="Click-Through Rate in % (clicks / impressions * 100)")
    cpa: float = Field(0.0, ge=0.0, description="Cost Per Acquisition (spend / purchases)")
    status: str = Field("TESTING", description="Evaluated status: WIN, LOSS, TESTING, PAUSED")
    streak: int = Field(0, description="Streak count: positive for WIN days (flame), negative for LOSS days (ice)")
    rank: Optional[int] = Field(None, description="Calculated rank on this date (1 = top)")
    rank_movement: Optional[str] = Field("NEW", description="Movement vs day before: UP_N, DOWN_N, SAME, NEW")


class DailySnapshotCreate(DailySnapshotBase):
    pass


class DailySnapshotInDB(DailySnapshotBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)


class LeaderboardItem(BaseModel):
    id: str = Field(..., description="Creative ID")
    name: str = Field(..., description="Creative Name")
    thumbnail_url: Optional[str] = None
    client_id: str
    client_name: str
    target_roas: float
    min_spend_threshold: float
    spend: float
    revenue: float
    purchases: int
    impressions: int
    clicks: int
    roas: float
    ctr: float
    cpa: float
    days_live: int
    status: str  # WIN, LOSS, TESTING, PAUSED
    streak: int  # e.g. 5 means 5 flame streak, -3 means 3 ice streak
    rank: int  # Current calculated rank
    yesterday_rank: Optional[int] = None
    rank_movement: str  # UP_2, DOWN_1, SAME, NEW
    rank_movement_val: int = 0  # +2, -1, 0
    first_seen_date: str
    headline: Optional[str] = None
    body_copy: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
