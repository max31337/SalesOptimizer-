from typing import Dict, Any, Optional, List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User
from app.schemas.user import UserUpdate
from app.crud.audit_log import log_user_action
from app.services.email import email_queue

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        query = self.db.query(User)
        
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return {
            "users": [self._format_user(user) for user in users],
            "total": total
        }

    def get_user_details(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._format_user(user)

    def update_user(self, user_id: int, user_update: UserUpdate, admin_id: int) -> Dict[str, str]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        changes = []
        update_dict = user_update.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_dict.items():
                if field == 'role' and value != user.role:
                    changes.append(f"role from '{user.role}' to '{value}'")
                elif field == 'is_active' and value != user.is_active:
                    status_change = "activated" if value else "deactivated"
                    changes.append(f"status {status_change}")
                setattr(user, field, value)
            
            if changes:
                log_user_action(
                    db=self.db,
                    user_id=user_id,
                    action="UPDATE_USER",
                    details=f"Updated user: {', '.join(changes)}",
                    performed_by=admin_id
                )
            
            self.db.commit()
            return {"message": "User updated successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def deactivate_user(self, user_id: int, admin_id: int) -> Dict[str, str]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role == "admin":
            admin_count = self.db.query(User).filter(
                User.role == "admin", 
                User.is_active == True
            ).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot deactivate the last admin user"
                )
        
        user.is_active = False
        log_user_action(
            db=self.db,
            user_id=user_id,
            action="DEACTIVATE_USER",
            details="User deactivated",
            performed_by=admin_id
        )
        
        self.db.commit()
        return {"message": "User successfully deactivated"}

    def verify_user(self, user_id: int) -> Dict[str, str]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = True
        user.verification_token = None
        
        try:
            self.db.commit()
            return {"message": "User verified successfully"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def _format_user(user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }