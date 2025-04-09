from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from app.api.auth.auth import get_current_user
from app.schemas.user import UserCreate, UserUpdate
from app.crud.user import create_user, update_user, get_users

router = APIRouter()

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/admin/users")
async def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    user = create_user(db, user_data)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }

@router.put("/admin/users/{user_id}")
async def update_user_details(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    updated_user = update_user(db, user_id, user_data)
    return {
        "message": "User updated successfully",
        "user": {
            "id": updated_user.id,
            "email": updated_user.email,
            "name": updated_user.name,
            "role": updated_user.role,
            "is_active": updated_user.is_active
        }
    }