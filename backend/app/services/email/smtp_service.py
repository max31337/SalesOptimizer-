from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from app.core.config import settings
from .interface import EmailServiceInterface
from .templates import EmailTemplate

class SMTPEmailService(EmailServiceInterface):
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.system_email = settings.SYSTEM_EMAIL

    async def send_email(self, to_email: str, subject: str, html_content: str) -> None:
        msg = MIMEMultipart('alternative')
        msg["Subject"] = subject
        msg["From"] = f"SalesOptimizer <{self.system_email}>"
        msg["To"] = to_email
        msg["Reply-To"] = self.system_email
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(self.system_email, to_email, msg.as_string())
                print(f"✅ Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            raise

    async def send_verification_email(self, email: str, token: str) -> None:
        verify_link = f"https://salesoptimizer.vercel.app/auth/verify.html?token={token}"
        html_content = EmailTemplate.verification_email(verify_link)
        await self.send_email(email, "Verify Your SalesOptimizer Account", html_content)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        reset_link = f"https://salesoptimizer.vercel.app/auth/resetpassword.html?token={token}"
        html_content = EmailTemplate.password_reset_email(reset_link)
        await self.send_email(email, "Password Reset Request - SalesOptimizer", html_content)

    async def send_invite_email(self, email: str, token: str) -> None:
        invite_link = f"https://salesoptimizer.vercel.app/auth/register.html?token={token}"
        html_content = EmailTemplate.invite_email(invite_link)
        await self.send_email(email, "You're Invited to SalesOptimizer!", html_content)