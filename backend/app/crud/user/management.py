from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password
from app.utils.token import generate_verification_token
from app.services.email import send_verification_email
from .base import UserRepository
from app.services.email import email_queue  # Add this import at the top

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

async def create_user(db: Session, user: UserCreate) -> User:
    """Create a new unverified user and send verification email."""
    repo = UserRepository(db)
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
        result = repo.commit_and_refresh(db_user)
        
        # Queue the verification email
        await email_queue.add_to_queue("verification", {
            "email": user.email,
            "token": verification_token
        })
        
        return result
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update user details."""
    repo = UserRepository(db)
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "password" and value:
            value = hash_password(value)
        setattr(db_user, key, value)
    
    try:
        return repo.commit_and_refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return True