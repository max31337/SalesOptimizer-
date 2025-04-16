import os
from dotenv import load_dotenv

load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email Settings
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/SalesOptimizerDB")


# Add to your BaseConfig class
FRONTEND_URL: str = "http://127.0.0.1:5050"
MAIL_PROVIDER: str = "mailtrap"

# Development config (config/development.py)
class DevelopmentConfig(BaseConfig):
    FRONTEND_URL: str = "http://127.0.0.1:5050"
    MAIL_PROVIDER: str = "mailtrap"
    # Mailtrap SMTP settings
    SMTP_SERVER: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USER: str = "your_mailtrap_user"
    SMTP_PASS: str = "your_mailtrap_pass"

# Production config (config/production.py) 
class ProductionConfig(BaseConfig):
    class BaseConfig:
        # Add mail configuration with defaults
        MAIL_PROVIDER: str = os.getenv("MAIL_PROVIDER", "mailtrap")
        MAILTRAP_SMTP_SERVER: str = os.getenv("MAILTRAP_SMTP_SERVER", "")
        MAILTRAP_SMTP_PORT: int = int(os.getenv("MAILTRAP_SMTP_PORT", 2525))
        MAILTRAP_SMTP_USER: str = os.getenv("MAILTRAP_SMTP_USER", "")
        MAILTRAP_SMTP_PASS: str = os.getenv("MAILTRAP_SMTP_PASS", "")
        MAILERSEND_SMTP_SERVER: str = os.getenv("MAILERSEND_SMTP_SERVER", "")
        MAILERSEND_SMTP_PORT: int = int(os.getenv("MAILERSEND_SMTP_PORT", 587))
        MAILERSEND_SMTP_USER: str = os.getenv("MAILERSEND_SMTP_USER", "")
        MAILERSEND_SMTP_PASS: str = os.getenv("MAILERSEND_SMTP_PASS", "")
        SYSTEM_EMAIL: str = os.getenv("SYSTEM_EMAIL", "noreply@salesoptimizer.com")
    # Mailersend SMTP settings
    SMTP_SERVER: str = "smtp.mailersend.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_mailersend_user"
    SMTP_PASS: str = "your_mailersend_key"