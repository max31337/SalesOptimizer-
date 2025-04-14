from pydantic_settings import BaseSettings
from typing import List
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    PROJECT_NAME: str = "SalesOptimizer"
    API_V1_PREFIX: str = "/api"
    ENV: Environment = Environment.DEVELOPMENT
    
    # Database
    DATABASE_URL: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SYSTEM_EMAIL: str
    
    # Security
    CORS_ORIGINS: List[str]

    class Config:
        case_sensitive = True
        env_file = ".env"