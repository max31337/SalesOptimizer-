import asyncio
from typing import Dict, Any
from .interface import EmailServiceInterface
from app.utils.security import generate_temp_password
from .email_types import EmailType
from .smtp_service import SMTPEmailService

class EmailQueueService:
    def __init__(self, email_service: EmailServiceInterface = None):
        self.queue = asyncio.Queue()
        self.email_service = email_service or SMTPEmailService()
        self.is_processing = False

    async def add_to_queue(self, email_type: EmailType, data: Dict[str, Any]) -> None:
        await self.queue.put({"type": email_type, "data": data})
        
        if not self.is_processing:
            asyncio.create_task(self.process_queue())

    async def process_queue(self) -> None:
        self.is_processing = True
        while not self.queue.empty():
            email_task = await self.queue.get()
            await self._process_email_task(email_task)
        self.is_processing = False

    async def _process_email_task(self, email_task: Dict[str, Any]):
        try:
            data = email_task["data"]
            email_type = email_task["type"]

            if email_type == EmailType.VERIFICATION:
                await self.email_service.send_verification_email(data["email"], data["token"])
            elif email_type == EmailType.PASSWORD_RESET:
                await self.email_service.send_password_reset_email(data["email"], data["token"])
            elif email_type == EmailType.INVITATION:
                temp_password = generate_temp_password()
                await self.email_service.send_invite_email(
                    email=data["email"],
                    token=data["token"],
                    temp_password=temp_password
                )
        except Exception as e:
            print(f"❌ Error processing email task: {e}")
            raise

# Create a singleton instance
email_queue = EmailQueueService()