from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENV: Environment = Environment.DEVELOPMENT
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # Email configuration
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SYSTEM_EMAIL: str = "noreply@salesoptimizer.com"