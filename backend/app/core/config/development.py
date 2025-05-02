from typing import List
from .base import BaseConfig, Environment
import os

class DevelopmentConfig(BaseConfig):
    ENV: Environment = Environment.DEVELOPMENT
    
    # Development-specific settings
    FRONTEND_URL: str = "http://127.0.0.1:5500"
    
    # Mailtrap SMTP settings
    MAIL_PROVIDER: str = "mailtrap"
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SYSTEM_EMAIL: str = os.getenv("SYSTEM_EMAIL", "system@salesoptimizer.com")
    
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ]

    class Config:
        env_file = ".env.development"
        case_sensitive = True