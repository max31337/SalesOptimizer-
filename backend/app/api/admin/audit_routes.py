from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import aliased
from app.db.database import get_db
from app.models.models import User, AuditLog  
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
    from_date: Optional[str] = None, 
    to_date: Optional[str] = None,    
    performed_by: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get audit logs with filtering and pagination"""

    UserTarget = aliased(User, name='user_target')
    UserPerformer = aliased(User, name='user_performer')
    
    query = (db.query(AuditLog, 
                     UserTarget.email.label('user_email'),
                     UserTarget.name.label('user_name'),
                     UserPerformer.email.label('performer_email'),
                     UserPerformer.name.label('performer_name'))
            .join(UserTarget, AuditLog.user_id == UserTarget.id)
            .join(UserPerformer, AuditLog.performed_by == UserPerformer.id))
    
    if from_date:
        query = query.filter(AuditLog.timestamp >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(AuditLog.timestamp <= datetime.fromisoformat(to_date))
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if performed_by:
        query = query.filter(AuditLog.performed_by == performed_by)

    total = query.count()
    results = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    logs_response = []
    for result in results:
        log_entry = {
            "timestamp": result.AuditLog.timestamp,
            "user_id": result.AuditLog.user_id,
            "user_email": result.user_email,
            "user_name": result.user_name,
            "action": result.AuditLog.action,
            "details": result.AuditLog.details,
            "performed_by": result.AuditLog.performed_by,
            "performer_name": result.performer_name,
            "performer_email": result.performer_email
        }
        logs_response.append(log_entry)
    
    return {
        "total": total,
        "logs": logs_response
    }