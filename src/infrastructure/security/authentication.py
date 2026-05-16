"""Custom DRF authentication using JWT."""
from __future__ import annotations
import importlib
_jwt = importlib.import_module("jwt")

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from src.infrastructure.database.models import UserORM


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[7:]
        try:
            payload = _jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except _jwt.ExpiredSignatureError:
            raise AuthenticationFailed("JWT token has expired.")
        except _jwt.InvalidTokenError:
            raise AuthenticationFailed("JWT token is invalid.")
        if payload.get("type") != "access":
            raise AuthenticationFailed("Invalid token type.")
        try:
            user = UserORM.objects.get(id=payload["sub"], is_active=True)
        except UserORM.DoesNotExist:
            raise AuthenticationFailed("User not found or inactive.")
        return (user, payload)
