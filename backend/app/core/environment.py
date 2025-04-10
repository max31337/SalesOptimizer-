from enum import Enum
from functools import lru_cache
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # fallback for older versions

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql+psycopg2://") + "?sslmode=require"
    ENV: Environment = Environment.DEVELOPMENT if not os.getenv("RAILWAY_ENVIRONMENT") else Environment.PRODUCTION
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str = "https://salesoptimizer.vercel.app"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://salesoptimizer.vercel.app",  # Remove trailing slash
        "https://noble-warmth-production.up.railway.app"
    ]
    
    SMTP_SERVER: str
    SMTP_PORT: str
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env.development" if not os.getenv("RAILWAY_ENVIRONMENT") else ".env.production"

@lru_cache()
def get_settings():
    return Settings()