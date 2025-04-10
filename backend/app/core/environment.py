from enum import Enum
from functools import lru_cache
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    ENV: Environment = Environment.DEVELOPMENT
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://salesoptimizer.vercel.app",
        "https://salesoptimizer-production.up.railway.app"  # Add Railway domain
    ]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()