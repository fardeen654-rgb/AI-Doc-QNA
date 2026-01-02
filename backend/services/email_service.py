import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email, subject, body):
    """Sends a transactional email using configured SMTP settings."""
    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        print("⚠️ Email not configured in .env, skipping notification.")
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        # Connect to server using TLS encryption
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"📧 Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")