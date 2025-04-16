from fastapi import BackgroundTasks
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio
import os
from app.core.config import settings

class EmailQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False

        # Use Mailtrap settings from config
        self.smtp_server = settings.MAILTRAP_SMTP_SERVER
        self.smtp_port = settings.MAILTRAP_SMTP_PORT
        self.smtp_username = settings.MAILTRAP_SMTP_USERNAME
        self.smtp_password = settings.MAILTRAP_SMTP_PASSWORD
        self.system_email = settings.SYSTEM_EMAIL

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
        msg["From"] = f"SalesOptimizer <{self.system_email}>"
        msg["To"] = to_email
        msg["Reply-To"] = self.system_email
        msg.attach(MIMEText(html_content, 'html'))

        try:
            async with asyncio.Lock():
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.system_email, to_email, msg.as_string())
                    print(f"✅ Email sent to {to_email} using {settings.ENV} configuration")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            raise

email_queue = EmailQueue()