from .interface import EmailServiceInterface
from .smtp_service import SMTPEmailService
from .queue_service import email_queue, EmailQueueService
from .templates import EmailTemplate

# Create an instance of the email service
email_service = SMTPEmailService()

# Export the email sending functions
async def send_verification_email(email: str, token: str):
    return await email_service.send_verification_email(email, token)

async def send_password_reset_email(email: str, token: str):
    return await email_service.send_password_reset_email(email, token)

async def send_invite_email(email: str, token: str, temp_password: str):
    return await email_service.send_invite_email(email, token, temp_password)

__all__ = [
    'EmailServiceInterface',
    'SMTPEmailService',
    'EmailQueueService',
    'email_queue',
    'EmailTemplate',
    'send_verification_email',
    'send_password_reset_email',
    'send_invite_email'
]