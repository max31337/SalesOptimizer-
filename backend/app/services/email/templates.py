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
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ 
                        margin: 0; 
                        font-family: 'Roboto', sans-serif; 
                        background-color: #f5f6fa;
                        color: #2d3436;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 2rem auto;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background-color: #7209B7;
                        padding: 1.5rem;
                        text-align: center;
                    }}
                    .content {{
                        padding: 2rem;
                    }}
                    .button {{
                        display: inline-block;
                        background-color: #7209B7;
                        color: white !important;
                        padding: 12px 24px;
                        border-radius: 4px;
                        text-decoration: none;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }}
                    .button:hover {{
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(114, 9, 183, 0.3);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="https://salesoptimizer.vercel.app/assets/images/logo.png" 
                             alt="SalesOptimizer Logo" 
                             style="height: 48px;">
                    </div>
                    <div class="content">
                        <h2 style="margin-top: 0; color: #2d3436;">You're Invited!</h2>
                        <p>Click below to complete your registration:</p>
                        <a href="{invite_link}" class="button">
                            Complete Registration
                        </a>
                        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #eee;">
                            <p style="font-size: 0.9rem; color: #636e72;">
                                Can't click the button? Copy this link:<br>
                                <a href="{invite_link}" style="color: #7209B7; word-break: break-all;">
                                    {invite_link}
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """
        return EmailTemplate.get_base_template(content)