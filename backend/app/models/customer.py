from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text)
    
    # Classification
    segment = Column(String, default="general")
    industry = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String, default="lead")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = Column(Integer, ForeignKey("users.id"))
    sales_rep = relationship("User", back_populates="customers")
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete")
    opportunities = relationship("Opportunity", back_populates="customer", cascade="all, delete")
    
    # Additional metadata
    notes = Column(Text)
    annual_revenue = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)