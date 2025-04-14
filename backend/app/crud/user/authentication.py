from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.utils.security import verify_password
from .management import get_user_by_email

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user