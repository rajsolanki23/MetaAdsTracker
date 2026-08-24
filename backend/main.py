import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import connect_to_mongo, close_mongo_connection
from backend.services.scheduler import start_scheduler, shutdown_scheduler
from backend.services.auth_service import get_current_admin

from backend.routers.health import router as health_router
from backend.routers.auth import router as auth_router
from backend.routers.clients import router as clients_router
from backend.routers.leaderboard import router as leaderboard_router
from backend.routers.creatives import router as creatives_router
from backend.routers.meta_sync import router as meta_sync_router
from backend.routers.import_export import router as import_router

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode...")
    await connect_to_mongo()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="High-performance Meta Ad Creative Leaderboard & Sync REST API with Single-Operator Security",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with robust regex support for Vercel, Render, and local development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$|^https:\/\/.*\.onrender\.com$|^http:\/\/localhost(:\d+)?$|^http:\/\/127\.0\.0\.1(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public Endpoints
app.include_router(health_router)
app.include_router(auth_router, prefix="/api")

# Protected Dashboard Endpoints (Require valid JWT Bearer token)
app.include_router(clients_router, dependencies=[Depends(get_current_admin)])
app.include_router(leaderboard_router, dependencies=[Depends(get_current_admin)])
app.include_router(creatives_router, dependencies=[Depends(get_current_admin)])
app.include_router(meta_sync_router, dependencies=[Depends(get_current_admin)])
app.include_router(import_router, dependencies=[Depends(get_current_admin)])


@app.get("/")
async def root():
    return {
        "message": "Creative Leaderboard API is active.",
        "docs": "/docs",
        "health": "/api/health",
        "auth": "/api/auth/login"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
