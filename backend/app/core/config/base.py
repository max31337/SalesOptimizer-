from enum import Enum
from typing import List
import os
from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    # Core settings
    ENV: Environment = Field(default=Environment.DEVELOPMENT, env="ENV")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # SMTP Settings
    MAIL_PROVIDER: str = Field(default="gmail", env="MAIL_PROVIDER")
    SMTP_SERVER: str = Field(..., env="SMTP_SERVER")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    SYSTEM_EMAIL: EmailStr = Field(..., env="SYSTEM_EMAIL")

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        extra = "ignore"