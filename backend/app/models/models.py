from sqlalchemy import Column, Integer, String, Boolean, DateTime  # Added DateTime
from app.db.database import Base  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="sales-rep")  # Now can be: "admin", "sales-rep", "analyst"
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, unique=True, nullable=True)
    invitation_token = Column(String, unique=True, nullable=True)
    reset_token = Column(String, unique=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)  


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)