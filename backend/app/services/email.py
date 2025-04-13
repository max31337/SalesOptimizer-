from mailersend import MailerSend
from mailersend.emails import NewEmail
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SYSTEM_EMAIL = "MS_Sqy4cV@test-q3enl6kjp5842vwr.mlsender.net"

def send_invite_email(email: str, token: str):
    """Send an invite email with token link."""
    
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are missing. Check .env file.")

    invite_link = f"https://salesoptimizer.vercel.app/auth/register.html?token={token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #7209B7; margin-bottom: 20px;">You're invited to join SalesOptimizer!</h2>
                <p>Click the button below to complete your registration:</p>
                <a href="{invite_link}" 
                   style="display: inline-block; 
                          background-color: #7209B7; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px; 
                          margin: 20px 0;">
                    Complete Registration
                </a>
            </div>
        </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg["Subject"] = "You're Invited to SalesOptimizer!"
    msg["From"] = f"SalesOptimizer <{SYSTEM_EMAIL}>"
    msg["To"] = email
    msg["Reply-To"] = SYSTEM_EMAIL
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SYSTEM_EMAIL, email, msg.as_string())
            print(f"✅ Invitation email sent to {email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        raise

def send_verification_email(email: str, token: str):
    """Send a verification email with token link."""
    
    if not SMTP_SERVER or not SMTP_USERNAME or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are missing. Check .env file.")

# Change this line
verify_link = f"https://salesoptimizer.vercel.app/auth/verify.html?token={token}"    
html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #7209B7; margin-bottom: 20px;">Welcome to SalesOptimizer!</h2>
                <p>Please verify your email by clicking the button below:</p>
                <a href="{verify_link}" 
                   style="display: inline-block; 
                          background-color: #7209B7; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px; 
                          margin: 20px 0;">
                    Verify Email
                </a>
                <p style="color: #666; font-size: 14px;">This link will expire in 24 hours.</p>
            </div>
        </body>
    </html>
    """
    
msg = MIMEMultipart('alternative')
msg["Subject"] = "Verify Your SalesOptimizer Account"
msg["From"] = f"SalesOptimizer <{SYSTEM_EMAIL}>"
msg["To"] = email
msg["Reply-To"] = SYSTEM_EMAIL

msg.attach(MIMEText(html_content, 'html'))

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            # Change this line
            SYSTEM_EMAIL = "MS_Sqy4cV@test-q3enl6kjp5842vwr.mlsender.net"
            print(f"✅ Verification email sent to {email}")
except Exception as e:
        print(f"❌ Error sending verification email: {e}")
        raise

