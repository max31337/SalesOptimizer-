from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import InteractionType

class InteractionBase(BaseModel):
    customer_id: int
    type: InteractionType
    subject: str
    description: str
    notes: Optional[str] = None
    interaction_date: datetime = datetime.utcnow()
    follow_up_date: Optional[datetime] = None
    follow_up_task: Optional[str] = None
    follow_up_status: str = "pending"
    sales_rep_id: int

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(InteractionBase):
    customer_id: Optional[int] = None
    type: Optional[InteractionType] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    interaction_date: Optional[datetime] = None
    follow_up_task: Optional[str] = None
    follow_up_status: Optional[str] = None
    sales_rep_id: Optional[int] = None

class Interaction(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True