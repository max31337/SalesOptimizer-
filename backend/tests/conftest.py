import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import Base, get_db
from app.main import app
from app.api.auth.auth import hash_password
from app.models import User

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_admin(db_session):
    admin = User(
        email="admin@test.com",
        password=hash_password("admin123"),
        name="Test Admin",
        username="testadmin",
        role="admin",
        is_active=True,
        is_verified=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def test_sales_rep(db_session):
    sales_rep = User(
        email="sales@test.com",
        password=hash_password("sales123"),
        name="Test Sales Rep",
        username="testsales",
        role="sales",
        is_active=True,
        is_verified=True
    )
    db_session.add(sales_rep)
    db_session.commit()
    return sales_rep