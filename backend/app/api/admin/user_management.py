from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from app.models.audit import AuditLog  # Update this import
from app.api.auth.auth import get_current_user
from pydantic import BaseModel
from app.crud.user import get_user
from app.crud.audit_log import log_user_action
from app.schemas.audit_log import AuditLogCreate  # Use this instead of creating a new model

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

# Remove this duplicate model since we're using the schema
# class AuditLog(BaseModel):
#     user_id: int
#     action: str
#     details: str
#     timestamp: datetime
#     performed_by: int

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/admin/users/", response_model=Dict[str, Any])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """List users with pagination, search, and filtering"""
    query = db.query(User)
    
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
    
    user_list = [
        {
            "id": user.id,
            "username": user.username, 
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
        for user in users
    ]
    
    return {
        "users": user_list,
        "total": total
    }

@router.get("/admin/users/{user_id}", response_model=Dict[str, Any])
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get a single user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }

class UserResponse(BaseModel):
    id: int
    name: str  
    email: str
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

@router.put("/admin/users/{user_id}", response_model=Dict[str, str])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    changes = []
    update_dict = user_update.model_dump(exclude_unset=True)
    
    try:
        # Apply updates and track changes
        for field, value in update_dict.items():
            if field == 'role' and value != user.role:
                changes.append(f"role from '{user.role}' to '{value}'")
            elif field == 'is_active' and value != user.is_active:
                status_change = "activated" if value else "deactivated"
                changes.append(f"status {status_change}")
            setattr(user, field, value)
        
        if changes:
            # Create audit log using the proper function
            log_user_action(
                db=db,
                user_id=user_id,
                action="UPDATE_USER",
                details=f"Updated user: {', '.join(changes)}",
                performed_by=current_user.id
            )
        
        db.commit()
        return {"message": "User updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Soft delete a user by setting is_active to False"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin", User.is_active == True).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
    
    db_user.is_active = False
    
    audit_log = AuditLog(
        user_id=user_id,
        action="delete",
        details="User deactivated",
        timestamp=datetime.utcnow(),
        performed_by=current_user.id
    )
    
    db.commit()
    return {"message": "User successfully deactivated"}