from enum import Enum
from functools import lru_cache
import os

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator  # Add missing imports
except ImportError:
    from pydantic import BaseSettings, Field, validator  # Fallback with all needed imports

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    CORS_ORIGINS: list = [
        "https://salesoptimizer.vercel.app",
        "http://localhost:3000",
        "http://crossover.proxy.rlwy.net:32542",
        "https://crossover.proxy.rlwy.net:32542"
    ]
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    @validator("DATABASE_URL")
    def fix_db_url(cls, v):
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1) + "?sslmode=require"
        return v
    ENV: Environment = Environment.DEVELOPMENT if not os.getenv("RAILWAY_ENVIRONMENT") else Environment.PRODUCTION
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://salesoptimizer.vercel.app")  # Changed from hardcoded value
    CORS_ORIGINS: list = [
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Dynamic origin
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