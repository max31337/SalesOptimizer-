from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Literal
from pydantic import BaseModel, EmailStr
from app.db.database import get_db
from app.models.models import User
from app.api.auth.auth import get_current_user, hash_password  # Add hash_password import
from app.services.email import send_invite_email
from app.utils.token import generate_verification_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: Literal["sales-rep", "analyst", "admin"]
    # Add name field with a default value
    name: str = "Invited User"  # Add this line

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Update this route
# Fix the route path by removing the /api prefix
@router.post("/admin/invite/")
async def invite_user(
    invite_data: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Send invitation to new user (admin only)"""
    invitation_token = generate_verification_token()
    
    # Store invitation token with temporary password
    temp_password = generate_verification_token()  # Generate a random temporary password
    new_invite = User(
        email=invite_data.email,
        role=invite_data.role,
        name=invite_data.name,
        username=invite_data.email.split('@')[0],
        password=hash_password(temp_password),  # Hash the temporary password
        is_active=False,
        is_verified=False,
        invitation_token=invitation_token
    )
    
    try:
        db.add(new_invite)
        db.commit()
        
        # Remove the await keyword here
        send_invite_email(invite_data.email, invitation_token)
        return {"message": f"Invitation sent to {invite_data.email}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Update this route too
@router.post("/admin/verify-user/{user_id}")
async def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Verify a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": f"User {user.email} has been verified"}

# Update the list_users function to include verification status
@router.get("/users/")
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return [{"id": user.id, "email": user.email, "role": user.role,
             "is_active": user.is_active, "is_verified": user.is_verified,
             "name": user.name} for user in users]


class AdminSettings(BaseModel):
    email_notifications: bool
    two_factor_auth: bool
    theme: str

@router.put("/admin/settings")
async def update_admin_settings(
    settings: AdminSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Update admin settings"""
    try:
        # Update user preferences in the database
        current_user.preferences = {
            "email_notifications": settings.email_notifications,
            "two_factor_auth": settings.two_factor_auth,
            "theme": settings.theme
        }
        db.commit()
        return {"message": "Settings updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))