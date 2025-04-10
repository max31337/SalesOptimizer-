from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    segment: Optional[str] = "general"
    industry: Optional[str] = None
    status: Optional[str] = "lead"
    notes: Optional[str] = None
    annual_revenue: Optional[int] = None
    employee_count: Optional[int] = None

class CustomerCreate(CustomerBase):
    assigned_to: Optional[int] = None

class CustomerUpdate(CustomerBase):
    is_active: Optional[bool] = None
    assigned_to: Optional[int] = None

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Changed from orm_mode
        # Remove this line completely: orm_mode = True