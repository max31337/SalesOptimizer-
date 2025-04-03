import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import User

def verify_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            admin.is_verified = True
            admin.verification_token = None
            db.commit()
            print(f"Admin user {admin.email} has been verified")
        else:
            print("No admin user found")
    finally:
        db.close()

if __name__ == "__main__":
    verify_admin()