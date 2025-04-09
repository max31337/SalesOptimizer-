from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    performed_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    performer = relationship("User", foreign_keys=[performed_by])

class LoginActivity(Base):
    __tablename__ = "login_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    success = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="login_activities")