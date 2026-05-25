"""Integration tests — Celery tasks."""
import pytest
from unittest.mock import patch, MagicMock

MOCK_MODULE = "src.infrastructure.external.tasks"


def make_smtp_mock():
    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
    return mock_smtp, mock_server


@pytest.mark.django_db
class TestSendWelcomeEmail:
    def test_send_welcome_email_success(self):
        from src.infrastructure.external.tasks import send_welcome_email

        mock_smtp, mock_server = make_smtp_mock()
        with patch("smtplib.SMTP", mock_smtp), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"):
            result = send_welcome_email.run("user-123", "testuser", "test@test.com")

        assert result is None
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "secret")
        mock_server.send_message.assert_called_once()

    def test_send_welcome_email_logs_info(self):
        from src.infrastructure.external.tasks import send_welcome_email

        mock_smtp, _ = make_smtp_mock()
        with patch("smtplib.SMTP", mock_smtp), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger:
            send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.info.assert_called_once_with("Welcome email sent to test@test.com")

    def test_send_welcome_email_retries_on_exception(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch("smtplib.SMTP", side_effect=Exception("SMTP error")), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger, \
             patch.object(send_welcome_email, "retry", side_effect=Exception("retry triggered")):
            with pytest.raises(Exception, match="retry triggered"):
                send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.exception.assert_called_once()

    def test_send_welcome_email_missing_env_vars(self):
        from src.infrastructure.external.tasks import send_welcome_email

        with patch.multiple(MOCK_MODULE, EMAIL_USER=None, EMAIL_PASSWORD=None), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger, \
             patch.object(send_welcome_email, "retry", side_effect=Exception("retry triggered")):
            with pytest.raises(Exception, match="retry triggered"):
                send_welcome_email.run("user-123", "testuser", "test@test.com")

        mock_logger.exception.assert_called_once()
        assert "EMAIL env variables are missing" in str(mock_logger.exception.call_args)


class TestNotifyNewFollower:
    def test_notify_new_follower_success(self):
        from src.infrastructure.external.tasks import notify_new_follower

        mock_smtp, mock_server = make_smtp_mock()
        with patch("smtplib.SMTP", mock_smtp), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"):
            result = notify_new_follower.run("user-456", "follower", "target@test.com")

        assert result is None
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "secret")
        mock_server.send_message.assert_called_once()

    def test_notify_new_follower_logs_info(self):
        from src.infrastructure.external.tasks import notify_new_follower

        mock_smtp, _ = make_smtp_mock()
        with patch("smtplib.SMTP", mock_smtp), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger:
            notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.info.assert_called_once_with("Follower notification sent to target@test.com")

    def test_notify_new_follower_with_different_users(self):
        from src.infrastructure.external.tasks import notify_new_follower

        mock_smtp, _ = make_smtp_mock()
        with patch("smtplib.SMTP", mock_smtp), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"):
            result = notify_new_follower.run("user-789", "anotheruser", "another@test.com")

        assert result is None

    def test_notify_new_follower_retries_on_exception(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch("smtplib.SMTP", side_effect=Exception("SMTP error")), \
             patch.multiple(MOCK_MODULE, EMAIL_USER="test@gmail.com", EMAIL_PASSWORD="secret"), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger, \
             patch.object(notify_new_follower, "retry", side_effect=Exception("retry triggered")):
            with pytest.raises(Exception, match="retry triggered"):
                notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.exception.assert_called_once()

    def test_notify_new_follower_missing_env_vars(self):
        from src.infrastructure.external.tasks import notify_new_follower

        with patch.multiple(MOCK_MODULE, EMAIL_USER=None, EMAIL_PASSWORD=None), \
             patch(f"{MOCK_MODULE}.logger") as mock_logger, \
             patch.object(notify_new_follower, "retry", side_effect=Exception("retry triggered")):
            with pytest.raises(Exception, match="retry triggered"):
                notify_new_follower.run("user-456", "follower", "target@test.com")

        mock_logger.exception.assert_called_once()
        assert "EMAIL env variables are missing" in str(mock_logger.exception.call_args)