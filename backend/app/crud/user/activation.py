from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User
from .base import UserRepository
from .management import get_user

def activate_user(db: Session, user_id: int) -> User:
    """Activate a user account."""
    repo = UserRepository(db)
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = True
    return repo.commit_and_refresh(db_user)

def deactivate_user(db: Session, user_id: int) -> User:
    """Deactivate a user account."""
    repo = UserRepository(db)
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    return repo.commit_and_refresh(db_user)