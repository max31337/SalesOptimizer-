from typing import List
from .base import BaseConfig, Environment

class ProductionConfig(BaseConfig):
    ENV: Environment = Environment.PRODUCTION
    
    # Production-specific settings
    FRONTEND_URL: str = "https://salesoptimizer.vercel.app"
    
    # MailerSend settings
    SMTP_SERVER: str = "smtp.mailersend.net"
    SMTP_PORT: int = 587
    SYSTEM_EMAIL: str = "noreply@salesoptimizer.com"
    
    CORS_ORIGINS: List[str] = [
        "https://salesoptimizer.vercel.app"
    ]

    class Config:
        env_file = ".env.production"