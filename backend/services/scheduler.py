import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.config import settings
from backend.services.sync_service import SyncService

logger = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler()

async def run_scheduled_sync():
    logger.info("Executing scheduled 4-hour Meta sync for all active clients...")
    try:
        sync_service = SyncService()
        results = await sync_service.sync_all_active_clients(sync_type="SCHEDULED")
        logger.info(f"Scheduled sync complete: {len(results)} clients processed.")
    except Exception as e:
        logger.error(f"Scheduled sync execution encountered error: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_scheduled_sync,
            trigger=IntervalTrigger(hours=settings.SYNC_INTERVAL_HOURS),
            id="meta_ad_sync_job",
            name="Meta Ad Creatives Periodic Sync",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"APScheduler started. Periodic sync configured every {settings.SYNC_INTERVAL_HOURS} hours.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
