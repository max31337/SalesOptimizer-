from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.models import AuditLog  # Update this import
from app.schemas.audit_log import AuditLogCreate, AuditLogFilter

def create_audit_log(db: Session, audit_log: AuditLogCreate) -> AuditLog:
    """Create a new audit log entry."""
    db_audit_log = AuditLog(**audit_log.dict())
    db.add(db_audit_log)
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log

def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[AuditLogFilter] = None
) -> List[AuditLog]:
    """Get audit logs with pagination and filtering."""
    query = db.query(AuditLog)

    if filters:
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        if filters.performed_by:
            query = query.filter(AuditLog.performed_by == filters.performed_by)
        if filters.from_date:
            query = query.filter(AuditLog.timestamp >= filters.from_date)
        if filters.to_date:
            query = query.filter(AuditLog.timestamp <= filters.to_date)

    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_audit_log(db: Session, audit_log_id: int) -> Optional[AuditLog]:
    """Get a specific audit log entry by ID."""
    return db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()

def get_user_audit_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
    """Get all audit logs for a specific user."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def log_user_action(
    db: Session,
    user_id: int,
    action: str,
    details: str,
    performed_by: int
) -> AuditLog:
    """Create an audit log entry for user actions"""
    audit_log = AuditLogCreate(
        user_id=user_id,
        action=action,
        details=details,
        timestamp=datetime.utcnow(),
        performed_by=performed_by
    )
    return create_audit_log(db, audit_log)