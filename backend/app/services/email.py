Yes, you can do that! The invite email can contain a special registration link that automatically fills in the invite token in the form when the user clicks it.


---

How It Works

1. Admin generates an invite → System sends an email.

# API example
# https://salesoptimizer.com/register?token=abcdef123456

def send_invite_email(email: str, token: str):
    """Send an invite email with a pre-filled token link."""
    invite_link = f"https://salesoptimizer.com/register?token={token}"
    msg = MIMEText(f"""
    You're invited to join SalesOptimizer!  
    Click the link below to register:  
    {invite_link}
    """)
    
    msg["Subject"] = "You're Invited to SalesOptimizer!"
    msg["From"] = SMTP_USERNAME
    msg["To"] = email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())

