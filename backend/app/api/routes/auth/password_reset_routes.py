from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import User
from app.schemas.user import PasswordReset, PasswordUpdate
from app.utils.token import generate_verification_token
from app.services.email.smtp_service import SMTPEmailService
from app.repositories.user_repository import UserRepository
from app.utils.security import get_password_hash
from app.core.exceptions import ValidationError

router = APIRouter()
email_service = SMTPEmailService()

@router.post("/forgot-password/")
async def request_password_reset(email_data: PasswordReset, db: Session = Depends(get_db)):
    """Initiate password reset process"""
    user = db.query(User).filter(User.email == email_data.email).first()
    
    if not user:
        return {"message": "If the email exists, a password reset link will be sent"}
    
    reset_token = generate_verification_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    try:
        db.commit()
        await email_service.send_password_reset_email(user.email, reset_token)
        return {"message": "If the email exists, a password reset link will be sent"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password/{token}")
async def reset_password(token: str, password_data: PasswordUpdate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    
    user = user_repo.get_by_reset_token(token)
    if not user or user.reset_token_expires < datetime.utcnow():
        raise ValidationError("Invalid or expired token")
    
    if password_data.password != password_data.confirm_password:
        raise ValidationError("Passwords do not match")
    
    try:
        user.password = get_password_hash(password_data.password)
        user.reset_token = None
        user.reset_token_expires = None
        user_repo.update(user)
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))