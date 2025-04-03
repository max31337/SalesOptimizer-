from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate
from app.api.auth.auth import hash_password, create_access_token

router = APIRouter()

@router.post("/auth/register-invited/")
def register_invited_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user who was invited by an admin"""
    if not user_data.invitation_token:
        raise HTTPException(status_code=400, detail="Invitation token is required")

    # Find the invitation record
    invite = db.query(User).filter(
        User.email == user_data.email,
        User.invitation_token == user_data.invitation_token,
        User.is_active == False
    ).first()

    if not invite:
        raise HTTPException(status_code=400, detail="Invalid invitation token or email")

    # Update the invited user's record
    invite.username = user_data.username
    invite.name = user_data.name
    invite.password = hash_password(user_data.password)
    invite.is_active = True
    invite.is_verified = True  # Auto-verify invited users
    invite.invitation_token = None  # Clear the invitation token

    try:
        db.commit()
        db.refresh(invite)

        # Generate JWT token for the new user
        access_token = create_access_token(data={"sub": invite.email})

        return {
            "msg": "Account created successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "name": invite.name,
            "role": invite.role,
            "is_verified": invite.is_verified
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))