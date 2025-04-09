from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditLog
from app.schemas.audit_log import AuditLogCreate

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, user_id: int, action: str, details: str, performed_by: int) -> AuditLog:
        audit_log = AuditLogCreate(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow(),
            performed_by=performed_by
        )
        db_audit_log = AuditLog(**audit_log.dict())
        self.db.add(db_audit_log)
        return db_audit_log

    def get_user_logs(self, user_id: int, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )