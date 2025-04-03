from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SYSTEM_EMAIL = "system@salesoptimizer.com"

def send_password_reset_email(email: str, token: str):
    """Send a password reset email with token link."""
    
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are missing. Check .env file.")

    reset_link = f"http://127.0.0.1:5500/salesoptimizer/auth/resetpassword.html?token={token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #7209B7; margin-bottom: 20px;">Password Reset Request</h2>
                <p>You've requested to reset your password. Click the button below to proceed:</p>
                <a href="{reset_link}" 
                   style="display: inline-block; 
                          background-color: #7209B7; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px; 
                          margin: 20px 0;">
                    Reset Password
                </a>
                <p>If you didn't request this, please ignore this email.</p>
                <p>This link will expire in 1 hour.</p>
            </div>
        </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg["Subject"] = "Password Reset Request - SalesOptimizer"
    msg["From"] = f"SalesOptimizer <{SYSTEM_EMAIL}>"
    msg["To"] = email
    msg["Reply-To"] = SYSTEM_EMAIL
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SYSTEM_EMAIL, email, msg.as_string())
            print(f"✅ Password reset email sent to {email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        raise