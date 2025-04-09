import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import User
from app.api.auth.auth import hash_password

def create_sales_rep():
    db = SessionLocal()
    try:
        # Check if sales rep already exists
        sales_rep = db.query(User).filter(User.email == "sales@salesoptimizer.com").first()
        if sales_rep:
            print("Sales representative already exists!")
            return
        
        # Create new sales rep
        sales_rep = User(
            name="Sales Representative",
            email="sales@salesoptimizer.com",
            username="salesrep",
            password=hash_password("sales123"),
            role="sales",
            is_active=True,
            is_verified=True
        )
        
        db.add(sales_rep)
        db.commit()
        print("Sales representative created successfully!")
        print("Email: sales@salesoptimizer.com")
        print("Password: sales123")
        
    except Exception as e:
        print(f"Error creating sales representative: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sales_rep()