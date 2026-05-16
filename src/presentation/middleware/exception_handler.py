"""Global exception handler — client never sees a stack trace."""

from __future__ import annotations
from datetime import datetime, timezone
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from src.domain.exceptions import DomainException
from src.application.services.auth_service import AuthenticationError, ConflictError
from src.application.services.post_service import NotFoundError, ForbiddenError


def global_exception_handler(exc, context):
    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    timestamp = datetime.now(timezone.utc).isoformat()

    if isinstance(exc, DomainException):
        return Response(
            {
                "status": 422,
                "error": "Domain Rule Violation",
                "message": str(exc),
                "timestamp": timestamp,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if isinstance(exc, AuthenticationError):
        return Response(
            {
                "status": 401,
                "error": "Unauthorized",
                "message": str(exc),
                "timestamp": timestamp,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if isinstance(exc, ConflictError):
        return Response(
            {
                "status": 409,
                "error": "Conflict",
                "message": str(exc),
                "timestamp": timestamp,
            },
            status=status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, NotFoundError):
        return Response(
            {
                "status": 404,
                "error": "Not Found",
                "message": str(exc),
                "timestamp": timestamp,
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    if isinstance(exc, ForbiddenError):
        return Response(
            {
                "status": 403,
                "error": "Forbidden",
                "message": str(exc),
                "timestamp": timestamp,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if response is not None:
        response.data = {
            "status": response.status_code,
            "error": _status_label(response.status_code),
            "message": _flatten_errors(response.data),
            "timestamp": timestamp,
        }
        return response

    return None


def _status_label(code: int) -> str:
    labels = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }
    return labels.get(code, "Error")


def _flatten_errors(data) -> str:
    if isinstance(data, dict):
        msgs = []
        for key, val in data.items():
            if isinstance(val, list):
                msgs.append(f"{key}: {', '.join(str(v) for v in val)}")
            else:
                msgs.append(str(val))
        return "; ".join(msgs)
    return str(data)
