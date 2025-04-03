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

class AuditLogResponse(AuditLogBase):
    id: int

    class Config:
        orm_mode = True

class AuditLogFilter(BaseModel):
    user_id: int | None = None
    action: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    performed_by: int | None = None