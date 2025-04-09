from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import AuditLog, User
from app.crud.audit_log import get_audit_logs
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
    # Join with User table to get user information
    logs = (
        db.query(AuditLog, User)
        .join(User, AuditLog.user_id == User.id)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Format the response
    formatted_logs = []
    for log, user in logs:
        performer = db.query(User).filter(User.id == log.performed_by).first()
        formatted_logs.append({
            "id": log.id,
            "timestamp": log.timestamp,
            "action": log.action,
            "details": log.details,
            "user_name": user.name,
            "user_email": user.email,
            "performer_name": performer.name if performer else "System",
            "performer_email": performer.email if performer else "system@example.com"
        })
    
    return formatted_logs