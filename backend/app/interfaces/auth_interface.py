from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models import User

class IAuthService(ABC):
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> User: pass

    @abstractmethod
    async def request_password_reset(self, email: str) -> str: pass

    @abstractmethod
    async def verify_reset_token(self, token: str) -> User: pass

    @abstractmethod
    async def reset_password(self, token: str, new_password: str) -> None: pass