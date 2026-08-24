from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CreativeBase(BaseModel):
    client_id: str = Field(..., description="Foreign key to Client")
    name: str = Field(..., description="Creative or ad name")
    meta_creative_id: Optional[str] = Field(None, description="Meta Graph API creative/ad ID")
    meta_ad_id: Optional[str] = Field(None, description="Meta Ad ID")
    thumbnail_url: Optional[str] = Field(None, description="Image or video thumbnail preview URL")
    body_copy: Optional[str] = Field(None, description="Primary ad copy text")
    headline: Optional[str] = Field(None, description="Ad headline")
    call_to_action: Optional[str] = Field("LEARN_MORE", description="CTA button type")
    status_override: Optional[str] = Field(None, description="Manual status override, e.g. PAUSED or None")
    notes: Optional[str] = Field(None, description="Operator notes/observations")
    tags: List[str] = Field(default_factory=list, description="Categorization tags, e.g. UGC, Founder, Test")
    is_archived: bool = Field(False, description="Archived flag")


class CreativeCreate(CreativeBase):
    pass


class CreativeUpdate(BaseModel):
    name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    body_copy: Optional[str] = None
    headline: Optional[str] = None
    call_to_action: Optional[str] = None
    status_override: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_archived: Optional[bool] = None


class CreativeInDB(CreativeBase):
    id: str = Field(..., alias="_id")
    first_seen_date: str = Field(..., description="YYYY-MM-DD when creative first spent")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
