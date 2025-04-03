from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.models import User, AuditLog  # Update this import
from app.api.auth.auth import get_current_user
from app.crud.audit_log import get_audit_logs
from app.schemas.audit_log import AuditLogResponse, AuditLogFilter

router = APIRouter()

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/audit-logs")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    from_date: Optional[str] = None,  # Changed from datetime to str
    to_date: Optional[str] = None,    # Changed from datetime to str
    performed_by: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get audit logs with filtering and pagination"""
    # Convert date strings to datetime objects if they're not empty
    from_datetime = datetime.fromisoformat(from_date) if from_date else None
    to_datetime = datetime.fromisoformat(to_date) if to_date else None
    
    filters = AuditLogFilter(
        user_id=user_id if user_id else None,
        action=action if action and action.strip() else None,
        from_date=from_datetime,
        to_date=to_datetime,
        performed_by=performed_by if performed_by else None
    )
    
    audit_logs = get_audit_logs(db, skip=skip, limit=limit, filters=filters)
    total = len(audit_logs)
    
    if total == 0:
        return {
            "total": 0,
            "logs": [],
            "message": "No audit logs found"
        }
    
    return {
        "total": total,
        "logs": audit_logs
    }