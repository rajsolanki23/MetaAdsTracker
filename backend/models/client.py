from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ClientBase(BaseModel):
    name: str = Field(..., description="Client or brand display name")
    meta_account_id: Optional[str] = Field(None, description="Meta Ad Account ID, e.g. act_123456789")
    access_token: Optional[str] = Field(None, description="Meta User or System User Access Token")
    target_roas: float = Field(2.5, ge=0.0, description="Target ROAS threshold for WIN evaluation")
    min_spend_threshold: float = Field(100.0, ge=0.0, description="Minimum spend ($) required to judge LOSS vs TESTING")
    currency: str = Field("USD", description="Account currency code")
    timezone: str = Field("America/New_York", description="Reporting timezone")
    is_active: bool = Field(True, description="Whether this client is active for syncs")


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    meta_account_id: Optional[str] = None
    access_token: Optional[str] = None
    target_roas: Optional[float] = None
    min_spend_threshold: Optional[float] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class ClientInDB(ClientBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ClientSummary(ClientInDB):
    blended_spend: float = 0.0
    blended_revenue: float = 0.0
    blended_roas: float = 0.0
    active_creatives_count: int = 0
    wins_count: int = 0
    losses_count: int = 0
    testing_count: int = 0
    paused_count: int = 0
    best_creative_name: Optional[str] = None
    best_creative_roas: Optional[float] = None
    worst_creative_name: Optional[str] = None
    worst_creative_roas: Optional[float] = None
    health_status: str = "HEALTHY"  # HEALTHY, WARNING, CRITICAL
