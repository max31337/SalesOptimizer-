from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import datetime
from passlib.context import CryptContext

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import Base, User
from app.core.config import DATABASE_URL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_dummy_users():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Clear existing users
    db.query(User).delete()
    
    # Create superadmin
    superadmin = User(
        username="superadmin",
        name="Super Admin",
        email="superadmin@salesoptimizer.com",
        password=pwd_context.hash("Admin123!"),
        role="admin",
        is_active=True,
        is_verified=True
    )
    db.add(superadmin)
    
    # Create 19 dummy users
    roles = ["user", "user", "user", "admin"]  # More users than admins
    for i in range(1, 20):
        role = roles[i % len(roles)]
        user = User(
            username=f"user{i}",
            name=f"Test User {i}",
            email=f"user{i}@example.com",
            password=pwd_context.hash(f"Password{i}!"),
            role=role,
            is_active=True,
            is_verified=True if role == "admin" else (i % 2 == 0)
        )
        db.add(user)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    create_dummy_users()