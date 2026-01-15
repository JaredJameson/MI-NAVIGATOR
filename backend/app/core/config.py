"""
MI-Navigator Configuration Settings
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "MI-Navigator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://minavigator:minavigator@localhost:5432/minavigator"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://minavigator:minavigator@localhost:5432/minavigator"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Claude AI
    ANTHROPIC_API_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # External APIs
    SIMILARWEB_API_KEY: str = ""
    SERPAPI_KEY: str = ""
    PROXYCURL_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
