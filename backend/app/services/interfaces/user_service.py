from abc import abstractmethod
from typing import Optional, Dict, Any
from .base import ServiceInterface
from app.models import User
from app.schemas.user import UserCreate, UserUpdate

class IUserService(ServiceInterface[User]):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> Dict[str, str]:
        pass

    @abstractmethod
    async def verify_user(self, user_id: int) -> User:
        pass