from enum import Enum
from functools import lru_cache
import os
from typing import List  # Add this import

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
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = [ 
        "https://salesoptimizer.vercel.app",
        "http://localhost:3000", 
        "http://localhost:8000"
    ]
    
    # Remove duplicate declarations
    SMTP_SERVER: str
    SMTP_PORT: int  # Changed to int type
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env.development" if not os.getenv("RAILWAY_ENVIRONMENT") else ".env.production"

@lru_cache()
def get_settings():
    return Settings()