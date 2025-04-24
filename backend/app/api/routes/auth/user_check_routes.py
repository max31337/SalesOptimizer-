from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from app.models import User
from app.core.auth import get_current_user  # Import from core.auth instead

router = APIRouter()

def get_sales_rep(current_user: User = Depends(get_current_user)):
    """Check if user is admin or sales rep"""
    if current_user.role not in ["admin", "sales-rep"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Only admins and sales representatives are allowed."
        )
    return current_user

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
        "role": current_user.role
    }
