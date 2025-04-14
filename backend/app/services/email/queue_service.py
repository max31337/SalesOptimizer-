import asyncio
from typing import Dict, Any
from .interface import EmailServiceInterface
from .smtp_service import SMTPEmailService

class EmailQueueService:
    def __init__(self, email_service: EmailServiceInterface = None):
        self.queue = asyncio.Queue()
        self.is_processing = False
        self.email_service = email_service or SMTPEmailService()

    async def add_to_queue(self, email_type: str, data: Dict[str, Any]) -> None:
        await self.queue.put({"type": email_type, "data": data})
        
        if not self.is_processing:
            asyncio.create_task(self.process_queue())

    async def process_queue(self) -> None:
        self.is_processing = True
        while not self.queue.empty():
            email_task = await self.queue.get()
            await self._process_email_task(email_task)
        self.is_processing = False

    async def _process_email_task(self, task: Dict[str, Any]) -> None:
        email_type = task["type"]
        data = task["data"]

        try:
            if email_type == "verification":
                await self.email_service.send_verification_email(data["email"], data["token"])
            elif email_type == "password_reset":
                await self.email_service.send_password_reset_email(data["email"], data["token"])
            elif email_type == "invite":
                await self.email_service.send_invite_email(data["email"], data["token"])
        except Exception as e:
            print(f"❌ Error processing email task: {e}")
            raise

# Create a singleton instance
email_queue = EmailQueueService()