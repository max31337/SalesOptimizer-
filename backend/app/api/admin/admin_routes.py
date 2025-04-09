from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Literal
from pydantic import BaseModel, EmailStr
from app.db.database import get_db
from app.models import User  # Updated import
from app.api.auth.auth import get_current_user, hash_password  
from app.services.email import send_invite_email
from app.utils.token import generate_verification_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: Literal["sales-rep", "analyst", "admin"]
    name: str = "Invited User" 

def check_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/admin/invite/")
async def invite_user(
    invite_data: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Send invitation to new user (admin only)"""
    invitation_token = generate_verification_token()
    
    temp_password = generate_verification_token() 
    new_invite = User(
        email=invite_data.email,
        role=invite_data.role,
        name=invite_data.name,
        username=invite_data.email.split('@')[0],
        password=hash_password(temp_password), 
        is_active=False,
        is_verified=False,
        invitation_token=invitation_token
    )
    
    try:
        db.add(new_invite)
        db.commit()
        
        send_invite_email(invite_data.email, invitation_token)
        return {"message": f"Invitation sent to {invite_data.email}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/admin/settings")
async def get_admin_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Get admin settings"""
    preferences = current_user.preferences or {}
    return {
        "email_notifications": preferences.get("email_notifications", False),
        "two_factor_auth": preferences.get("two_factor_auth", False),
        "theme": preferences.get("theme", "light")
    }

#still working on this functionality
@router.post("/admin/setup-2fa")
async def setup_two_factor_auth(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
):
    """Setup 2FA for admin"""
    import pyotp
    import qrcode
    import base64
    from io import BytesIO

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    provisioning_uri = totp.provisioning_uri(current_user.email, issuer_name="SalesOptimizer")
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    current_user.totp_secret = secret
    db.commit()
    
    return {"qr_code": qr_code}