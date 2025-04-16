from abc import ABC, abstractmethod
from typing import Optional

class EmailServiceInterface(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str) -> None:
        pass

    @abstractmethod
    async def send_verification_email(self, email: str, token: str) -> None:
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, token: str) -> None:
        pass

    @abstractmethod
    async def send_invite_email(self, email: str, token: str, temp_password: str) -> None:  # Fixed signature
        pass