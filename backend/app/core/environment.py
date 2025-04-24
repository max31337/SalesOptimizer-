from enum import Enum
from functools import lru_cache
import os
from typing import List

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    from pydantic import BaseSettings, Field, validator

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    ENV: Environment = Environment.DEVELOPMENT
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = Field("http://127.0.0.1:5500", env="FRONTEND_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    SYSTEM_EMAIL: str = Field("system@salesoptimizer.com", env="SYSTEM_EMAIL")

    class Config:
        env_file = ".env.development" if os.getenv("ENV", "development").lower() == "development" else ".env.production"
        case_sensitive = True
        extra = "allow"  # This line fixes the validation error

@lru_cache()
def get_settings() -> Settings:
    return Settings()