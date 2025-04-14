from .interface import EmailServiceInterface
from .smtp_service import SMTPEmailService
from .queue_service import email_queue, EmailQueueService
from .templates import EmailTemplate
from .email_service import send_verification_email, send_password_reset_email

__all__ = [
    'EmailServiceInterface',
    'SMTPEmailService',
    'EmailQueueService',
    'email_queue',
    'EmailTemplate',
    "send_verification_email",
    "send_password_reset_email"
]