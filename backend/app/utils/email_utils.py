# backend/app/utils/email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(recipient_email: str, subject: str, html_content: str, text_content: str):
    """
    A generic function to send an email.
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print("WARN: Email settings are not configured. Cannot send email.")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.MAIL_FROM
    message["To"] = recipient_email

    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, recipient_email, message.as_string())
        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_password_reset_email(recipient_email: str, reset_link: str):
    """Sends a password reset email to the user."""
    subject = "Reset Your Password"
    text = f"""Hi, Click the link to reset your password: {reset_link}"""
    html = f"""
    <html><body>
        <p>Hi,<br>
           Please click the button below to reset your password:
        </p>
        <a href="{reset_link}" style="background-color:#1E90FF; color:white; padding:15px 25px; text-align:center; text-decoration:none; display:inline-block; border-radius:5px;">
            Reset Your Password
        </a>
    </body></html>
    """
    send_email(recipient_email, subject, html, text)