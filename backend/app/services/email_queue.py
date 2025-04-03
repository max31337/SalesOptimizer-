from fastapi import BackgroundTasks
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio
from app.core.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

SYSTEM_EMAIL = "system@salesoptimizer.com"

class EmailQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False

    async def add_email(self, to_email: str, subject: str, html_content: str):
        await self.queue.put({
            "to": to_email,
            "subject": subject,
            "html_content": html_content
        })
        
        if not self.is_processing:
            asyncio.create_task(self.process_queue())

    async def process_queue(self):
        self.is_processing = True
        while not self.queue.empty():
            email_data = await self.queue.get()
            await self.send_email(
                email_data["to"],
                email_data["subject"],
                email_data["html_content"]
            )
        self.is_processing = False

    async def send_email(self, to_email: str, subject: str, html_content: str):
        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject
        msg["From"] = f"SalesOptimizer <{SYSTEM_EMAIL}>"
        msg["To"] = to_email
        msg["Reply-To"] = SYSTEM_EMAIL
        msg.attach(MIMEText(html_content, 'html'))

        try:
            async with asyncio.Lock():
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SYSTEM_EMAIL, to_email, msg.as_string())
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            raise

email_queue = EmailQueue()