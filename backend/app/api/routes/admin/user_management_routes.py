from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from app.schemas.user import UserUpdate
from app.middleware.admin import admin_required
from app.services.admin_service import AdminService


router = APIRouter()

# Remove /admin prefix from individual routes since it's handled by the parent router
@router.get("/users/list", response_model=Dict[str, Any])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """List users with pagination, search, and filtering"""
    admin_service = AdminService(db)
    return admin_service.list_users(skip, limit, search, role, is_active)

@router.get("/users/details/{user_id}", response_model=Dict[str, Any])
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Get a single user by ID"""
    admin_service = AdminService(db)
    return admin_service.get_user_details(user_id)

@router.put("/users/update/{user_id}", response_model=Dict[str, str])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Update user details"""
    admin_service = AdminService(db)
    return admin_service.update_user(user_id, user_update, current_user.id)

@router.delete("/users/deactivate/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Soft delete a user by setting is_active to False"""
    admin_service = AdminService(db)
    return admin_service.deactivate_user(user_id, current_user.id)

@router.post("/verify-user/{user_id}")
async def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Verify a user account"""
    admin_service = AdminService(db)
    return admin_service.verify_user(user_id)