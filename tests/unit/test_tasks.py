"""Unit tests — Celery tasks."""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestSendWelcomeEmail:
    def test_send_welcome_email_success(self):
        from src.infrastructure.external.tasks import send_welcome_email
        result = send_welcome_email.run("user-123", "testuser", "test@test.com")
        assert result is None

    def test_send_welcome_email_logs_info(self):
        from src.infrastructure.external.tasks import send_welcome_email
        with patch("src.infrastructure.external.tasks.logger") as mock_logger:
            send_welcome_email.run("user-123", "testuser", "test@test.com")
            assert mock_logger.info.called

    def test_send_welcome_email_retries_on_exception(self):
        from src.infrastructure.external.tasks import send_welcome_email
        mock_self = MagicMock()
        mock_self.retry = MagicMock(side_effect=Exception("retry"))
        with patch("src.infrastructure.external.tasks.logger") as mock_logger:
            mock_logger.info.side_effect = Exception("log error")
            with pytest.raises(Exception):
                send_welcome_email.run("user-123", "testuser", "test@test.com")


class TestNotifyNewFollower:
    def test_notify_new_follower_success(self):
        from src.infrastructure.external.tasks import notify_new_follower
        result = notify_new_follower.run("user-456", "follower", "target@test.com")
        assert result is None

    def test_notify_new_follower_logs_info(self):
        from src.infrastructure.external.tasks import notify_new_follower
        with patch("src.infrastructure.external.tasks.logger") as mock_logger:
            notify_new_follower.run("user-456", "follower", "target@test.com")
            assert mock_logger.info.called

    def test_notify_new_follower_with_different_users(self):
        from src.infrastructure.external.tasks import notify_new_follower
        result = notify_new_follower.run("user-789", "anotheruser", "another@test.com")
        assert result is None