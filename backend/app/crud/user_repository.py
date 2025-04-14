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
        user_data = user_in.model_dump()
        user_data["password"] = get_password_hash(user_data["password"])
        return self.create(user_data)

    def update_with_hash(self, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            if update_data["password"] != update_data.get("confirm_password"):
                raise ValidationError("Passwords do not match")
            update_data["password"] = get_password_hash(update_data["password"])
        return self.update(user, update_data)