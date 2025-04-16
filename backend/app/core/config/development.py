import os
from typing import List
from .base import BaseConfig, Environment

class DevelopmentConfig(BaseConfig):
    ENV: Environment = Environment.DEVELOPMENT
    FRONTEND_URL: str = "http://127.0.0.1:5050"
    MAIL_PROVIDER: str = "mailtrap"
    
    # Updated Mailtrap SMTP settings
    SMTP_SERVER: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USERNAME: str = "0da5f8344f06e8"  # Your provided username
    SMTP_PASSWORD: str = "c22d57e063d34f"  # Use your actual password
    SYSTEM_EMAIL: str = "noreply@salesoptimizer.com"

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:5500",  # Add this line for your development server
        "http://localhost:5500"
    ]

    class Config:
        env_file = ".env.development"
        case_sensitive = True