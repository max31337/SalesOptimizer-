from enum import Enum
from functools import lru_cache
import os
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator, EmailStr
except ImportError:
    from pydantic import BaseSettings, Field, validator, EmailStr

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    # Core settings
    ENV: Environment = Field(default=Environment.DEVELOPMENT, env="ENV")
    
    @validator('ENV', pre=True)
    def validate_environment(cls, v, values):
        # Check if running on Railway
        is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
        
        # If on Railway, use production regardless of host
        if is_railway:
            return Environment.PRODUCTION
            
        # Otherwise, use development for local environment
        return Environment.DEVELOPMENT
        
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = Field(..., env="FRONTEND_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=3, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # SMTP Settings
    SMTP_SERVER: str = Field(..., env="SMTP_SERVER")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    SYSTEM_EMAIL: EmailStr = Field(..., env="SYSTEM_EMAIL")

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file_mapping = {
            'development': '.env.development',
            'production': '.env.production',
            'testing': '.env.test'
        }
        current_env = os.getenv("ENV", "development").lower()
        env_file = env_file_mapping.get(current_env, '.env.development')
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    print(f"Loading settings for ENV: {os.getenv('ENV', 'development')}")
    print(f"Using env_file: {Settings.Config.env_file}")
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise

settings = get_settings()