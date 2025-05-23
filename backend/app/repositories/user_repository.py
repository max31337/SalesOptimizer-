from sqlalchemy.orm import Session
from app.models import User
from app.core.exceptions import ValidationError
from app.utils.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_reset_token(self, token: str) -> User:
        return self.db.query(User).filter(User.reset_token == token).first()

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user