from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from .base import BaseRepository
from app.utils.security import get_password_hash

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_with_hash(self, user_in: UserCreate) -> User:
        # Remove confirm_password and get username from email if not provided
        user_data = user_in.model_dump(exclude={'confirm_password'})
        if 'username' not in user_data or not user_data['username']:
            user_data['username'] = user_data['email'].split('@')[0]
        
        user_data["password"] = get_password_hash(user_data["password"])
        
        # Create new user instance
        user = User(**user_data)
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            # Make a copy of the user data before closing the session
            self.db.expunge(user)
            return user
        finally:
            self.db.close()

    def update_with_hash(self, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            if update_data["password"] != update_data.get("confirm_password"):
                raise ValidationError("Passwords do not match")
            update_data["password"] = get_password_hash(update_data["password"])
        return self.update(user, update_data)