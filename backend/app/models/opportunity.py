from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property  # Change this import
from app.db.database import Base
from datetime import datetime
from app.models.enums import OpportunityStage

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    deal_value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    stage = Column(Enum(OpportunityStage), nullable=False, default=OpportunityStage.LEAD)
    probability = Column(Float, default=0)
    expected_close_date = Column(DateTime, nullable=False)
    closed_date = Column(DateTime, nullable=True)  
    predicted_probability = Column(Float)
    predicted_close_date = Column(DateTime)
    confidence_score = Column(Float)
    risk_factors = Column(Text)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    sales_rep = relationship("User", back_populates="opportunities")
    
    # Change from @property to @hybrid_property
    _customer_name = None
    
    @hybrid_property
    def customer_name(self):
        if self._customer_name is not None:
            return self._customer_name
        return self.customer.name if self.customer else None
    
    @customer_name.setter
    def customer_name(self, value):
        self._customer_name = value
    
    class Config:
        orm_mode = True

