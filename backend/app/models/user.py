from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)  
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    invitation_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    audit_logs = relationship("AuditLog", foreign_keys="[AuditLog.user_id]", back_populates="user")
    performed_actions = relationship("AuditLog", foreign_keys="[AuditLog.performed_by]", back_populates="performer")
    login_activities = relationship("LoginActivity", back_populates="user", cascade="all, delete")
    interactions = relationship("Interaction", back_populates="sales_rep")
    customers = relationship("Customer", back_populates="sales_rep")
    opportunities = relationship("Opportunity", back_populates="sales_rep")
    sales = relationship("Sale", back_populates="user")