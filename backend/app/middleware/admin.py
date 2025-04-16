from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models import User

async def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user