# /backend/app/utils.py (Updated for Gmail SMTP)

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from .config import settings

async def send_email(subject: str, recipients: list, body: str):
    """A reusable utility function for sending emails with Gmail SMTP."""
    
    # Create connection configuration for Gmail
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html"
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"Email sent successfully to {recipients}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
