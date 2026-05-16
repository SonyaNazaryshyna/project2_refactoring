"""Async Celery tasks for background processing."""
from __future__ import annotations
import logging
from src.infrastructure.external.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, user_id: str, username: str, email: str):
    """Send welcome email to newly registered user."""
    try:
        logger.info(f"Sending welcome email to {email} (user_id={user_id})")
        # In production: use django.core.mail.send_mail or an SMTP provider
        # send_mail(
        #     subject="Welcome to Microblog!",
        #     message=f"Hi {username}, welcome!",
        #     from_email="noreply@microblog.io",
        #     recipient_list=[email],
        # )
        logger.info(f"Welcome email sent to {email}")
    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def notify_new_follower(self, target_user_id: str, follower_username: str, target_email: str):
    """Notify user that someone followed them."""
    try:
        logger.info(f"Notifying {target_email} about new follower @{follower_username}")
        # In production: send push notification / email
        logger.info("Notification sent.")
    except Exception as exc:
        raise self.retry(exc=exc)
