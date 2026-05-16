"""Tests for global exception handler."""
from unittest.mock import Mock
from datetime import datetime

from src.presentation.middleware.exception_handler import (
    global_exception_handler,
    _status_label,
    _flatten_errors,
)
from src.domain.exceptions import DomainException
from src.application.services.auth_service import AuthenticationError, ConflictError
from src.application.services.post_service import NotFoundError, ForbiddenError


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_context():
    return {"request": Mock(), "view": Mock()}


# ══════════════════════════════════════════
# _status_label
# ══════════════════════════════════════════

class TestStatusLabel:
    def test_400(self): assert _status_label(400) == "Bad Request"
    def test_401(self): assert _status_label(401) == "Unauthorized"
    def test_403(self): assert _status_label(403) == "Forbidden"
    def test_404(self): assert _status_label(404) == "Not Found"
    def test_405(self): assert _status_label(405) == "Method Not Allowed"
    def test_500(self): assert _status_label(500) == "Internal Server Error"
    def test_unknown_returns_error(self): assert _status_label(999) == "Error"
    def test_422_returns_error(self): assert _status_label(422) == "Error"


# ══════════════════════════════════════════
# _flatten_errors
# ══════════════════════════════════════════

class TestFlattenErrors:
    def test_string_input(self):
        assert _flatten_errors("simple error") == "simple error"

    def test_dict_with_list_values(self):
        data = {"email": ["This field is required."]}
        result = _flatten_errors(data)
        assert "email" in result
        assert "This field is required." in result

    def test_dict_with_string_values(self):
        data = {"detail": "Not found"}
        result = _flatten_errors(data)
        assert "Not found" in result

    def test_dict_multiple_keys(self):
        data = {"email": ["Invalid"], "username": ["Too short"]}
        result = _flatten_errors(data)
        assert "email" in result
        assert "username" in result

    def test_dict_multiple_list_items(self):
        data = {"password": ["Too short", "No digits"]}
        result = _flatten_errors(data)
        assert "Too short" in result
        assert "No digits" in result

    def test_non_dict_non_string(self):
        result = _flatten_errors(42)
        assert result == "42"

    def test_empty_dict(self):
        result = _flatten_errors({})
        assert result == ""

    def test_nested_values_stringified(self):
        data = {"field": 123}
        result = _flatten_errors(data)
        assert "123" in result


# ══════════════════════════════════════════
# global_exception_handler — custom exceptions
# ══════════════════════════════════════════

class TestDomainExceptionHandler:
    def test_returns_422(self):
        exc = DomainException("Post content cannot be empty.")
        response = global_exception_handler(exc, make_context())
        assert response.status_code == 422

    def test_error_field(self):
        exc = DomainException("Some rule violated.")
        response = global_exception_handler(exc, make_context())
        assert response.data["error"] == "Domain Rule Violation"

    def test_message_field(self):
        exc = DomainException("Like count cannot go below zero.")
        response = global_exception_handler(exc, make_context())
        assert response.data["message"] == "Like count cannot go below zero."

    def test_status_field(self):
        exc = DomainException("err")
        response = global_exception_handler(exc, make_context())
        assert response.data["status"] == 422

    def test_timestamp_present(self):
        exc = DomainException("err")
        response = global_exception_handler(exc, make_context())
        assert "timestamp" in response.data
        assert response.data["timestamp"] is not None


class TestAuthenticationErrorHandler:
    def test_returns_401(self):
        exc = AuthenticationError("Invalid email or password.")
        response = global_exception_handler(exc, make_context())
        assert response.status_code == 401

    def test_error_field(self):
        exc = AuthenticationError("Invalid email or password.")
        response = global_exception_handler(exc, make_context())
        assert response.data["error"] == "Unauthorized"

    def test_message_field(self):
        exc = AuthenticationError("Account is deactivated.")
        response = global_exception_handler(exc, make_context())
        assert response.data["message"] == "Account is deactivated."

    def test_status_field(self):
        exc = AuthenticationError("err")
        response = global_exception_handler(exc, make_context())
        assert response.data["status"] == 401


class TestConflictErrorHandler:
    def test_returns_409(self):
        exc = ConflictError("Email is already taken.")
        response = global_exception_handler(exc, make_context())
        assert response.status_code == 409

    def test_error_field(self):
        exc = ConflictError("Email is already taken.")
        response = global_exception_handler(exc, make_context())
        assert response.data["error"] == "Conflict"

    def test_message_field(self):
        exc = ConflictError("Username is already taken.")
        response = global_exception_handler(exc, make_context())
        assert response.data["message"] == "Username is already taken."

    def test_status_field(self):
        exc = ConflictError("err")
        response = global_exception_handler(exc, make_context())
        assert response.data["status"] == 409


class TestNotFoundErrorHandler:
    def test_returns_404(self):
        exc = NotFoundError("Post not found.")
        response = global_exception_handler(exc, make_context())
        assert response.status_code == 404

    def test_error_field(self):
        exc = NotFoundError("Post not found.")
        response = global_exception_handler(exc, make_context())
        assert response.data["error"] == "Not Found"

    def test_message_field(self):
        exc = NotFoundError("User 'ghost' not found.")
        response = global_exception_handler(exc, make_context())
        assert response.data["message"] == "User 'ghost' not found."

    def test_status_field(self):
        exc = NotFoundError("err")
        response = global_exception_handler(exc, make_context())
        assert response.data["status"] == 404


class TestForbiddenErrorHandler:
    def test_returns_403(self):
        exc = ForbiddenError("You can only edit your own posts.")
        response = global_exception_handler(exc, make_context())
        assert response.status_code == 403

    def test_error_field(self):
        exc = ForbiddenError("You can only edit your own posts.")
        response = global_exception_handler(exc, make_context())
        assert response.data["error"] == "Forbidden"

    def test_message_field(self):
        exc = ForbiddenError("You can only delete your own posts.")
        response = global_exception_handler(exc, make_context())
        assert response.data["message"] == "You can only delete your own posts."

    def test_status_field(self):
        exc = ForbiddenError("err")
        response = global_exception_handler(exc, make_context())
        assert response.data["status"] == 403


# ══════════════════════════════════════════
# DRF native exceptions (passed through)
# ══════════════════════════════════════════

class TestDRFExceptionPassthrough:
    def test_drf_404_reformatted(self):
        from rest_framework.exceptions import NotFound
        exc = NotFound("Not found.")
        response = global_exception_handler(exc, make_context())
        assert response is not None
        assert response.data["status"] == 404
        assert response.data["error"] == "Not Found"
        assert "timestamp" in response.data

    def test_drf_401_reformatted(self):
        from rest_framework.exceptions import AuthenticationFailed
        exc = AuthenticationFailed("JWT expired.")
        response = global_exception_handler(exc, make_context())
        assert response is not None
        assert response.data["status"] == 401

    def test_drf_403_reformatted(self):
        from rest_framework.exceptions import PermissionDenied
        exc = PermissionDenied("Permission denied.")
        response = global_exception_handler(exc, make_context())
        assert response is not None
        assert response.data["status"] == 403

    def test_drf_405_reformatted(self):
        from rest_framework.exceptions import MethodNotAllowed
        exc = MethodNotAllowed("POST")
        response = global_exception_handler(exc, make_context())
        assert response is not None
        assert response.data["status"] == 405
        assert response.data["error"] == "Method Not Allowed"

    def test_drf_validation_error_reformatted(self):
        from rest_framework.exceptions import ValidationError
        exc = ValidationError({"email": ["This field is required."]})
        response = global_exception_handler(exc, make_context())
        assert response is not None
        assert "email" in response.data["message"]
        assert "timestamp" in response.data


# ══════════════════════════════════════════
# Unknown exceptions
# ══════════════════════════════════════════

class TestUnknownExceptions:
    def test_unknown_exception_returns_none(self):
        exc = ValueError("Something unexpected")
        response = global_exception_handler(exc, make_context())
        assert response is None

    def test_runtime_error_returns_none(self):
        exc = RuntimeError("crash")
        response = global_exception_handler(exc, make_context())
        assert response is None

    def test_exception_returns_none(self):
        exc = Exception("generic")
        response = global_exception_handler(exc, make_context())
        assert response is None


# ══════════════════════════════════════════
# Timestamp format
# ══════════════════════════════════════════

class TestTimestamp:
    def test_timestamp_is_iso_format(self):
        exc = DomainException("err")
        response = global_exception_handler(exc, make_context())
        ts = response.data["timestamp"]
        # Should parse without error
        datetime.fromisoformat(ts)

    def test_timestamp_has_timezone(self):
        exc = DomainException("err")
        response = global_exception_handler(exc, make_context())
        ts = response.data["timestamp"]
        assert "+" in ts or ts.endswith("Z") or "+00:00" in ts