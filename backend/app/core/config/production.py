import os
from typing import List
from .base import BaseConfig, Environment

class ProductionConfig(BaseConfig):
    ENV: Environment = Environment.PRODUCTION
    
    # Production-specific settings
    FRONTEND_URL: str = "https://salesoptimizer.vercel.app"
    
    # Gmail SMTP settings
    MAIL_PROVIDER: str = "gmail"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SYSTEM_EMAIL: str = os.getenv("SYSTEM_EMAIL")
    
    CORS_ORIGINS: List[str] = [
        "https://salesoptimizer.vercel.app"
    ]

    class Config:
        env_file = ".env.production"
        case_sensitive = True