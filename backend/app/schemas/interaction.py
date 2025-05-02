from pydantic import BaseModel
from typing import Optional, List
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
    follow_up_status: str = "Scheduled"
    customer_name: Optional[str] = None  # Add this line

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(InteractionBase):
    customer_id: Optional[int] = None
    type: Optional[InteractionType] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    interaction_date: Optional[datetime] = None
    follow_up_tasks: Optional[List[str]] = []     
    follow_up_status: Optional[str] = None
    sales_rep_id: Optional[int] = None

class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    sales_rep_id: int

    class Config:
        from_attributes = True