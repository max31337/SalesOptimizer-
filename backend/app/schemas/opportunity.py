from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import OpportunityStage

class OpportunityBase(BaseModel):
    title: str
    deal_value: float  # Changed from value to deal_value to match the model
    currency: str = "USD"
    stage: OpportunityStage
    probability: float = 0
    expected_close_date: datetime
    customer_id: int

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(OpportunityBase):
    title: Optional[str] = None
    deal_value: Optional[float] = None  # Changed from value to deal_value
    currency: Optional[str] = None
    stage: Optional[OpportunityStage] = None
    probability: Optional[float] = None
    expected_close_date: Optional[datetime] = None
    customer_id: Optional[int] = None

class Opportunity(OpportunityBase):
    id: int
    sales_rep_id: int
    predicted_probability: Optional[float] = None
    predicted_close_date: Optional[datetime] = None
    confidence_score: Optional[float] = None
    risk_factors: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True