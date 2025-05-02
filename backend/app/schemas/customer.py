from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
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
    annual_revenue: Optional[int] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = True  # Add this field to match the model's default

class CustomerCreate(CustomerBase):
    assigned_to: Optional[int] = None

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    assigned_to: Optional[int] = None

# schemas/customer.py
class CustomerSchema(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    assigned_to: Optional[int]

    class Config:
        from_attributes = True  # Changed from orm_mode
        # Remove this line completely: orm_mode = True