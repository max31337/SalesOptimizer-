from typing import Union  # Add this import
from pydantic import BaseModel
from datetime import datetime

class AuditLogBase(BaseModel):
    user_id: int
    action: str
    details: str
    timestamp: datetime
    performed_by: int

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogFilter(BaseModel):
    user_id: Union[int, None] = None  # Changed from int | None
    action: Union[str, None] = None
    from_date: Union[datetime, None] = None
    to_date: Union[datetime, None] = None
    performed_by: Union[int, None] = None

class AuditLogResponse(AuditLogBase):
    id: int

    class Config:
        from_attributes = True  # Changed from orm_mode = True