from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Creative Leaderboard API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "creative_leaderboard"

    # Authentication & Security
    JWT_SECRET_KEY: str = "leaderboard-secure-jwt-secret-key-2026-auth-32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 14 days session
    ADMIN_EMAIL: str = "rajsolanki32@gmail.com"
    ADMIN_PASSWORD_HASH: str = "pbkdf2_sha256$100000$15f918365567d0f5ba54a7f033b30780$b878fe118a08ec3aa275d1ea9c5a89d31ba16c84af9e08d98b16d2e0a3c0314c"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app"
    ]

    # Meta API
    META_API_VERSION: str = "v18.0"
    META_GRAPH_API_VERSION: str = "v18.0"
    META_GRAPH_BASE_URL: str = "https://graph.facebook.com"
    META_GRAPH_API_BASE_URL: str = "https://graph.facebook.com"

    # Cron / Scheduler
    CRON_SECRET: str = "leaderboard-secret-cron-key"
    SYNC_INTERVAL_HOURS: int = 4

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
