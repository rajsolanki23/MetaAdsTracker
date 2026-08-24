from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Creative Leaderboard API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # MongoDB Atlas or Local connection string
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "creative_leaderboard"

    # CORS settings - allows local frontend & production Vercel domains
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,https://*.vercel.app"

    # Meta Graph API Base URL & Version
    META_GRAPH_API_VERSION: str = "v18.0"
    META_GRAPH_API_BASE_URL: str = "https://graph.facebook.com"

    # Cron / Webhook Secret for triggered syncs
    CRON_SECRET: Optional[str] = "leaderboard-secret-cron-key"

    # Background sync interval in hours
    SYNC_INTERVAL_HOURS: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
