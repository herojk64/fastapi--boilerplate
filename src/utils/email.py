import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")


def is_email_configured() -> bool:
    """Check if email is configured."""
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_email(
    to: List[str],
    subject: str,
    body: str,
    html: bool = False,
    from_email: Optional[str] = None
) -> bool:
    """Send email using SMTP."""
    if not is_email_configured():
        return False
    
    try:
        msg = MIMEMultipart()
        msg["From"] = from_email or SMTP_FROM
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html" if html else "plain"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception:
        return False


def send_password_reset_email(email: str, reset_token: str, base_url: str) -> bool:
    """Send password reset email."""
    reset_link = f"{base_url}/reset-password?token={reset_token}"
    
    html_body = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """
    
    return send_email(
        to=[email],
        subject="Password Reset Request",
        body=html_body,
        html=True
    )


def send_welcome_email(email: str, username: str) -> bool:
    """Send welcome email to new users."""
    html_body = f"""
    <html>
        <body>
            <h2>Welcome {username}!</h2>
            <p>Your account has been created successfully.</p>
            <p>Thank you for joining us!</p>
        </body>
    </html>
    """
    
    return send_email(
        to=[email],
        subject="Welcome!",
        body=html_body,
        html=True
    )
