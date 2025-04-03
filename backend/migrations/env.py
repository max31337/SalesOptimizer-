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
db_url = os.getenv("DATABASE_URL", "postgresql://postgres@localhost/SalesOptimizerDB")

# Ensure proper postgresql:// prefix
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")

config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
