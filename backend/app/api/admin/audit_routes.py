from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import AuditLog, User
from app.api.auth.auth import get_current_user
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/audit-logs")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    logs = db.query(AuditLog).offset(skip).limit(limit).all()
    return logs  # Return the list directly instead of dict