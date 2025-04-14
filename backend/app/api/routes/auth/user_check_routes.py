from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.models import User
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def get_current_user_details(current_user: User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active
    }

@router.get("/check-session")
async def check_session(current_user: User = Depends(get_current_user)):
    return {
        "valid": True, 
        "is_active": current_user.is_active,
        "role": current_user.role  # Add role to response
    }
