from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.exceptions import AuthenticationError, ValidationError
from app.models import User
from app.utils.security import verify_password, get_password_hash
from app.utils.token import generate_verification_token
from app.core.auth import create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise AuthenticationError("Invalid credentials")
            
        if not verify_password(password, user.password):
            raise AuthenticationError("Invalid credentials")
            
        if not user.is_active:
            raise AuthorizationError("Account inactive")
            
        return user

    async def request_password_reset(self, email: str) -> None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return
            
        reset_token = generate_verification_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        self.db.commit()
        
        return reset_token

    async def verify_reset_token(self, token: str) -> User:
        user = self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise ValidationError("Invalid or expired reset token")
            
        return user

    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self.verify_reset_token(token)
        user.password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()