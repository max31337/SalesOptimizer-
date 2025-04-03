from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv
from app.models.models import Base

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ... rest of your env.py file ...