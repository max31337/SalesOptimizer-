from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from pydantic import BaseModel, EmailStr
from typing import List, Literal
from app.api.auth.auth import get_current_user, hash_password  # Added hash_password import
from app.schemas.user import UserCreate, UserUpdate, InviteUser  # Add InviteUser import
from app.crud.user import create_user, update_user, get_users
from app.utils.token import generate_verification_token
from app.services.email import send_invite_email

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

class InviteUserRequest(BaseModel):
     email: EmailStr
     role: Literal["sales-rep", "analyst", "admin"]
     name: str = "Invited User"  # Add this line

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
 