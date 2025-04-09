from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import User  # Updated import
from app.schemas.user import PasswordReset, PasswordUpdate
from app.api.auth.auth import hash_password
from app.utils.token import generate_verification_token
from app.services.password_reset_email import send_password_reset_email  # Updated import

router = APIRouter()

@router.post("/auth/forgot-password/")
def request_password_reset(email_data: PasswordReset, db: Session = Depends(get_db)):
    """Initiate password reset process"""
    user = db.query(User).filter(User.email == email_data.email).first()
    
    if not user:
        return {"message": "If the email exists, a password reset link will be sent"}
    
    reset_token = generate_verification_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    try:
        db.commit()
        send_password_reset_email(user.email, reset_token)
        return {"message": "If the email exists, a password reset link will be sent"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/reset-password/{token}")
def reset_password(token: str, password_data: PasswordUpdate, db: Session = Depends(get_db)):
    """Reset password using the token"""
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user.password = hash_password(password_data.password)
    user.reset_token = None
    user.reset_token_expires = None
    
    try:
        db.commit()
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))