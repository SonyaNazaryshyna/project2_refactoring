"""Integration tests — Celery tasks."""
import pytest
from unittest.mock import patch, MagicMock


EMAIL_ENVS = {
    "src.infrastructure.external.tasks.EMAIL_USER": "test@gmail.com",
    "src.infrastructure.external.tasks.EMAIL_PASSWORD": "secret",
}


@pytest.mark.django_db
class TestSendWelcomeEmail:
    def test_send_welcome_email_success(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch("smtplib.SMTP") as mock_smtp, \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = send_welcome_email.run("user-123", "testuser", "test@test.com")

        assert result is None
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "secret")
        mock_server.send_message.assert_called_once()

    def test_send_welcome_email_logs_info(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch("smtplib.SMTP") as mock_smtp, \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.info.assert_called_once_with("Welcome email sent to test@test.com")

    def test_send_welcome_email_retries_on_exception(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch("smtplib.SMTP", side_effect=Exception("SMTP error")), \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            mock_self = MagicMock()
            mock_self.retry = MagicMock(side_effect=Exception("retry triggered"))

            with patch.object(send_welcome_email, "retry", side_effect=Exception("retry triggered")):
                with pytest.raises(Exception, match="retry triggered"):
                    send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.exception.assert_called_once()

    def test_send_welcome_email_missing_env_vars(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch("src.infrastructure.external.tasks.EMAIL_USER", None), \
             patch("src.infrastructure.external.tasks.EMAIL_PASSWORD", None), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            with patch.object(send_welcome_email, "retry", side_effect=Exception("retry triggered")):
                with pytest.raises(Exception, match="retry triggered"):
                    send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.exception.assert_called_once()
        assert "EMAIL env variables are missing" in str(
            mock_logger.exception.call_args
        )


class TestNotifyNewFollower:
    def test_notify_new_follower_success(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("smtplib.SMTP") as mock_smtp, \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_new_follower.run("user-456", "follower", "target@test.com")

        assert result is None
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "secret")
        mock_server.send_message.assert_called_once()

    def test_notify_new_follower_logs_info(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("smtplib.SMTP") as mock_smtp, \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.info.assert_called_once_with(
            "Follower notification sent to target@test.com"
        )

    def test_notify_new_follower_with_different_users(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("smtplib.SMTP") as mock_smtp, \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = notify_new_follower.run("user-789", "anotheruser", "another@test.com")

        assert result is None

    def test_notify_new_follower_retries_on_exception(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("smtplib.SMTP", side_effect=Exception("SMTP error")), \
             patch.multiple("src.infrastructure.external.tasks", **EMAIL_ENVS), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            with patch.object(notify_new_follower, "retry", side_effect=Exception("retry triggered")):
                with pytest.raises(Exception, match="retry triggered"):
                    notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.exception.assert_called_once()

    def test_notify_new_follower_missing_env_vars(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("src.infrastructure.external.tasks.EMAIL_USER", None), \
             patch("src.infrastructure.external.tasks.EMAIL_PASSWORD", None), \
             patch("src.infrastructure.external.tasks.logger") as mock_logger:
            with patch.object(notify_new_follower, "retry", side_effect=Exception("retry triggered")):
                with pytest.raises(Exception, match="retry triggered"):
                    notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.exception.assert_called_once()
        assert "EMAIL env variables are missing" in str(
            mock_logger.exception.call_args
        )