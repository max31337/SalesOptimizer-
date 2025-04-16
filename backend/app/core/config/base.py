from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Add this line
    ENV: Environment = Environment.DEVELOPMENT
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"