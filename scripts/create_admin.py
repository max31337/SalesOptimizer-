import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import User
from app.api.auth.auth import hash_password

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print("❌ Admin user already exists!")
            return

        # Create new admin user
        admin_user = User(
            username="admin",
            name="Administrator",
            email="admin@salesoptimizer.com",
            password=hash_password("admin123"),  # Change this password!
            role="admin",
            is_active=True,
            is_verified=True
        )

        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("\n⚠️ Please change the password after first login!")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()