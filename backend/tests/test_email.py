import asyncio
import pytest
from app.services.email.smtp_service import SMTPEmailService
from app.core.config import settings

@pytest.mark.asyncio
async def test_mailtrap_connection():
    email_service = SMTPEmailService()
    test_email = "test@example.com"
    
    print("\nSMTP Configuration:")
    print(f"Server: {settings.SMTP_SERVER}")
    print(f"Port: {settings.SMTP_PORT}")
    print(f"Username: {settings.SMTP_USERNAME}")
    
    try:
        await email_service.send_email(
            to_email=test_email,
            subject=f"Test Email from SalesOptimizer ({asyncio.get_event_loop().time()})",
            html_content=f"""
            <html>
                <body>
                    <h1>Test Email</h1>
                    <p>If you see this in Mailtrap, the email configuration is working!</p>
                    <p>Time: {asyncio.get_event_loop().time()}</p>
                </body>
            </html>
            """
        )
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_invite_email():
    email_service = SMTPEmailService()
    test_email = "test@example.com"
    test_token = "test-token-123"
    test_password = "TempPass123!"
    
    try:
        await email_service.send_invite_email(
            email=test_email,
            token=test_token,
            temp_password=test_password
        )
        print("\n✅ Invite email sent successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Error sending invite email: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Mailtrap connection...")
    result = asyncio.run(test_mailtrap_connection())
    if result:
        print("✅ Test email sent successfully! Check your Mailtrap inbox.")
    else:
        print("❌ Failed to send test email.")