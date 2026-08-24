from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SyncLogBase(BaseModel):
    client_id: Optional[str] = Field(None, description="Client ID or null for all-client sync")
    client_name: Optional[str] = Field(None, description="Client display name")
    status: str = Field(..., description="SUCCESS, PARTIAL, FAILED")
    records_synced: int = Field(0, description="Count of creative snapshots updated/inserted")
    duration_ms: int = Field(0, description="Sync execution duration in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    sync_type: str = Field("SCHEDULED", description="SCHEDULED, MANUAL, BULK_IMPORT")


class SyncLogInDB(SyncLogBase):
    id: str = Field(..., alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
