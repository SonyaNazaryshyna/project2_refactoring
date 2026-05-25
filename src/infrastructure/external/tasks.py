"""Async Celery tasks for background processing."""

from __future__ import annotations
import logging
import os
import smtplib
from email.mime.text import MIMEText
from src.infrastructure.external.celery_app import celery_app

logger = logging.getLogger(__name__)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, user_id: str, username: str, email: str):
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            raise ValueError("EMAIL env variables are missing")
        msg = MIMEText(
            f"""
        Hi {username}! 👋

        Welcome to Microblog 🚀

        We’re happy to have you here.

        You can now:
        • create posts 📝
        • follow other users 👥
        • interact with the community 💬

        Enjoy your experience!

        — Microblog Team
        """
        )
        msg["Subject"] = "👋 Welcome to Microblog!"
        msg["From"] = EMAIL_USER
        msg["To"] = email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Welcome email sent to {email}")

    except Exception as exc:
        logger.exception(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def notify_new_follower(self, target_user_id: str, follower_username: str, target_email: str):
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            raise ValueError("EMAIL env variables are missing")

        msg = MIMEText(
            f"""
            Hi 👋

            Good news!

            @{follower_username} just started following you 🎉

            Log in to your account to check their profile and stay connected.

            — Microblog Team
            """
        )

        msg["Subject"] = f"👥 New follower: @{follower_username}"
        msg["From"] = EMAIL_USER
        msg["To"] = target_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Follower notification sent to {target_email}")

    except Exception as exc:
        logger.exception(f"Failed to send follower notification: {exc}")
        raise self.retry(exc=exc)
