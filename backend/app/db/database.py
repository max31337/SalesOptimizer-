from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine with proper error handling
try:
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True  # Enable connection health checks
    )
except Exception as e:
    print(f"Error connecting to database: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
