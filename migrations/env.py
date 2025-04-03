from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv
from app.models.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config

config.set_main_option("sqlalchemy.url", DATABASE_URL)

