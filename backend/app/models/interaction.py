from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from app.models.enums import InteractionType

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(InteractionType), nullable=False)
    subject = Column(String, nullable=False) 
    description = Column(Text, nullable=False)  # Main content of the interaction
    notes = Column(Text)
    interaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_task = Column(Text, nullable=True)
    follow_up_status = Column(String, default="pending")
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    sales_rep = relationship("User", back_populates="interactions")