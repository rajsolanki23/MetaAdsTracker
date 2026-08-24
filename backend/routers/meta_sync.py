from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.database import get_database
from backend.models.sync_log import SyncLogInDB
from backend.services.meta_client import MetaClient, MetaAPIError
from backend.services.sync_service import SyncService

router = APIRouter(prefix="/api/meta", tags=["Meta Integration"])


class TestConnectionRequest(BaseModel):
    meta_account_id: str = Field(..., description="Ad Account ID, e.g. act_123456789")
    access_token: str = Field(..., description="Meta Access Token")


@router.post("/test-connection")
async def test_meta_connection(payload: TestConnectionRequest):
    """
    Validates Meta Ad Account ID and Access Token against Meta Graph API v18.0.
    """
    client = MetaClient()
    try:
        result = await client.test_connection(
            account_id=payload.meta_account_id,
            access_token=payload.access_token
        )
        return result
    except MetaAPIError as e:
        raise HTTPException(status_code=e.status_code or 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error validating connection: {str(e)}")


@router.post("/sync/{client_id}")
async def trigger_client_sync(
    client_id: str,
    target_date: Optional[str] = Query(None, description="Optional target date YYYY-MM-DD (defaults to today)")
):
    """
    Triggers an immediate on-demand synchronization for a specific client account.
    """
    sync_service = SyncService()
    result = await sync_service.sync_client(
        client_id=client_id,
        target_date=target_date,
        sync_type="MANUAL"
    )
    if result.get("status") == "FAILED":
        raise HTTPException(status_code=400, detail=result.get("error", "Sync failed"))
    return result


@router.post("/sync-all")
async def trigger_all_clients_sync():
    """
    Triggers an immediate on-demand synchronization for all active client accounts.
    """
    sync_service = SyncService()
    results = await sync_service.sync_all_active_clients(sync_type="MANUAL")
    return {
        "status": "COMPLETED",
        "total_clients": len(results),
        "results": results
    }


@router.get("/logs", response_model=List[SyncLogInDB])
async def get_sync_logs(
    limit: int = Query(50, ge=1, le=200, description="Max logs to retrieve"),
    client_id: Optional[str] = Query(None, description="Filter logs by client ID")
):
    """
    Returns audit log records of recent automated and manual Meta API synchronizations.
    """
    db = get_database()
    query = {}
    if client_id:
        query["client_id"] = client_id
        
    cursor = db.sync_logs.find(query).sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    results = []
    for d in docs:
        d["_id"] = str(d["_id"])
        results.append(SyncLogInDB(**d))
    return results
