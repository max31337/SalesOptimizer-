from typing import List
from .base import BaseConfig, Environment

class DevelopmentConfig(BaseConfig):
    ENV: Environment = Environment.DEVELOPMENT
    
    # Development-specific settings
    FRONTEND_URL: str = "http://127.0.0.1:5500"
    
    # Mailtrap settings
    SMTP_SERVER: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 587
    SYSTEM_EMAIL: str = "noreply@salesoptimizer.local"
    
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",  # Added missing comma
        "http://localhost:8000"
    ]

    class Config:
        env_file = ".env.development"