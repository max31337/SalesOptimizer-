from app.core.config import settings
from app.utils.email_templates import get_verification_email_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email: str, token: str) -> None:
    """Send email verification email"""
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = email
    msg['Subject'] = "Verify your email"
    
    body = get_verification_email_template(token)
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset email"""
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"
    
    body = f"""
    <html>
        <body>
            <h1>Password Reset</h1>
            <p>Click the link below to reset your password:</p>
            <a href="http://localhost:8000/api/auth/reset-password/{token}">
                Reset Password
            </a>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)