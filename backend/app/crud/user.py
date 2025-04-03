from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from fastapi import HTTPException

from app.models.models import User
from app.schemas.user import UserCreate
from app.api.auth.auth import hash_password, verify_password
from app.utils.token import generate_verification_token
from app.services.email import send_verification_email

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new unverified user and send verification email."""
    try:
        hashed_password = hash_password(user.password)
        verification_token = generate_verification_token()
        
        db_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            role=user.role,
            is_verified=False,
            verification_token=verification_token
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

def verify_user_email(db: Session, token: str) -> User:
    """Verify user email using token."""
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Invalid verification token"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )
    
    user.is_verified = True
    user.verification_token = None  # Clear the token after verification
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, user_data: dict) -> User:
    """Update user details."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "password" in user_data:
        user_data["password"] = hash_password(user_data["password"])
    
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def deactivate_user(db: Session, user_id: int) -> User:
    """Deactivate a user account."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_user(db: Session, user_id: int) -> User:
    """Activate a user account."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user