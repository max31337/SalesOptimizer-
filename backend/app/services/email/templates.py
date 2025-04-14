from typing import Dict

class EmailTemplate:
    @staticmethod
    def get_base_template(content: str) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    {content}
                </div>
            </body>
        </html>
        """

    @staticmethod
    def verification_email(verify_link: str) -> str:
        content = f"""
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
        """
        return EmailTemplate.get_base_template(content)

    @staticmethod
    def password_reset_email(reset_link: str) -> str:
        content = f"""
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
        """
        return EmailTemplate.get_base_template(content)

    @staticmethod
    def invite_email(invite_link: str) -> str:
        content = f"""
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
        """
        return EmailTemplate.get_base_template(content)