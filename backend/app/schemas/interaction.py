from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

class InteractionType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"

class InteractionBase(BaseModel):
    type: InteractionType
    notes: Optional[str] = None
    interaction_date: datetime
    follow_up_date: Optional[datetime] = None
    follow_up_task: Optional[str] = None
    follow_up_status: Optional[str] = "pending"
    customer_id: int
    sales_rep_id: int

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(BaseModel):
    type: Optional[InteractionType] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    follow_up_task: Optional[str] = None
    follow_up_status: Optional[str] = None

class Interaction(InteractionBase):
    id: int
    
    class Config:
        orm_mode = True