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
    ENV: Environment = Environment.DEVELOPMENT if not os.getenv("RAILWAY_ENVIRONMENT") else Environment.PRODUCTION
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://salesoptimizer.vercel.app/",  # Add your Vercel URL here
        "https://salesoptimizer-production.up.railway.app"
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