import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from app.core.config import settings
from .interface import EmailServiceInterface
from .templates import EmailTemplate
from urllib.parse import urljoin

class SMTPEmailService(EmailServiceInterface):
    def __init__(self):
        self.env = settings.ENV or "production"
        self.base_url = (
            "http://127.0.0.1:5500"  # Local development
            if self.env == "development" 
            else "https://salesoptimizer.vercel.app"  # Production
        )
        
        # Use SMTP settings from config
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USERNAME
        self.smtp_pass = settings.SMTP_PASSWORD
        self.system_email = settings.SYSTEM_EMAIL

    async def send_email(self, to_email: str, subject: str, html_content: str) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"SalesOptimizer <{self.system_email}>"
        msg['To'] = to_email
        msg['Reply-To'] = self.system_email
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            print(f"📧 Attempting to send email to {to_email}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)  # Set to 1 for less verbose output
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                print(f"✅ Email sent successfully to {to_email}")
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            print(f"❌ SMTP settings: {self.smtp_server}:{self.smtp_port}")
            raise

    async def send_verification_email(self, email: str, token: str) -> None:
        verify_link = f"{self.base_url}/auth/verify.html?token={token}"
        html_content = EmailTemplate.verification_email(verify_link)
        await self.send_email(email, "Verify Your SalesOptimizer Account", html_content)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        reset_link = f"{self.base_url}/auth/resetpassword.html?token={token}"
        html_content = EmailTemplate.password_reset_email(reset_link)
        await self.send_email(email, "Password Reset Request - SalesOptimizer", html_content)

    async def send_invite_email(self, email: str, token: str, temp_password: str) -> None:
        invite_link = f"{self.base_url}/auth/register.html?token={token}"
        html_content = EmailTemplate.invite_email(invite_link)  # Single argument now
        await self.send_email(email, "SalesOptimizer Invitation", html_content)