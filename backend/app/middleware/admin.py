from fastapi import Depends, HTTPException
from app.api.auth.auth import get_current_user
from app.models import User

class AdminMiddleware:
    @staticmethod
    async def verify_admin(current_user: User = Depends(get_current_user)):
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user

admin_required = AdminMiddleware.verify_admin