from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timezone
from backend.config import settings
from backend.services.sync_service import SyncService

router = APIRouter(prefix="/api", tags=["Health & Cron"])


@router.get("/health")
async def health_check():
    """
    Keep-alive endpoint for Render free tier and health monitoring.
    """
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/sync/cron")
async def trigger_cron_sync(x_cron_secret: str = Header(None)):
    """
    Public webhook endpoint triggered by external cron services (e.g. Cron-Job.org / UptimeRobot).
    Keeps Render service active and runs 4-hour scheduled syncs.
    """
    if settings.CRON_SECRET and x_cron_secret != settings.CRON_SECRET:
        # If secret is set, validate it (fallback allows open if in dev)
        if settings.ENVIRONMENT != "development":
            raise HTTPException(status_code=401, detail="Invalid cron secret")

    sync_service = SyncService()
    results = await sync_service.sync_all_active_clients(sync_type="SCHEDULED")
    return {
        "status": "SUCCESS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "clients_processed": len(results),
        "results": results
    }
