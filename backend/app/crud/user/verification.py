from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User
from .base import UserRepository

def verify_user_email(db: Session, token: str) -> User:
    """Verify user email using token."""
    repo = UserRepository(db)
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    user.is_verified = True
    user.verification_token = None 
    return repo.commit_and_refresh(user)