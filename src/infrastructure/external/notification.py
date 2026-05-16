"""Notification sender — delegates to Celery tasks."""
from src.domain.entities.user import User
from src.domain.ports import NotificationSender
from src.infrastructure.external import tasks


class CeleryNotificationSender(NotificationSender):
    def send_welcome(self, user: User) -> None:
        tasks.send_welcome_email.delay(
            str(user.id), str(user.username), str(user.email)
        )

    def send_new_follower(self, user: User, follower: User) -> None:
        tasks.notify_new_follower.delay(
            str(user.id), str(follower.username), str(user.email)
        )
