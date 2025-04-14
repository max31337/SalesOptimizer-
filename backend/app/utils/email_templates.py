def get_verification_email_template(token: str) -> str:
    """Generate email verification template"""
    return f"""
    <html>
        <body>
            <h1>Email Verification</h1>
            <p>Please click the link below to verify your email:</p>
            <a href="http://localhost:8000/api/auth/verify/{token}">
                Verify Email
            </a>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """