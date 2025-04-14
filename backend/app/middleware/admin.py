from fastapi import Depends, HTTPException
from app.core.auth import get_current_user  # Changed import path
from app.models import User

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user