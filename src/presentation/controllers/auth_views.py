"""Auth REST controllers."""

import importlib

_jwt = importlib.import_module("jwt")

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.conf import settings

from src.application.dtos import RegisterRequest, LoginRequest
from src.presentation.config.container import get_auth_service, get_jwt_provider

@extend_schema(tags=["Auth"], summary="Register new user")
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    if not request.data:
        return Response({"message": "Request body is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        req = RegisterRequest(**request.data)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    tokens = get_auth_service().register(req)
    return Response(tokens.model_dump(), status=status.HTTP_201_CREATED)


@extend_schema(tags=["Auth"], summary="Login")
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    if not request.data:
        return Response({"message": "Request body is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        req = LoginRequest(**request.data)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    tokens = get_auth_service().login(req)
    return Response(tokens.model_dump(), status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"], summary="Refresh access token")
@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh = request.data.get("refresh_token")
    if not refresh:
        return Response({"message": "refresh_token is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = _jwt.decode(refresh, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return Response({"message": "Invalid token type"}, status=status.HTTP_400_BAD_REQUEST)
        tokens = get_jwt_provider().create_tokens(payload["sub"], role="ROLE_USER")
        return Response({"access_token": tokens.access_token})
    except _jwt.ExpiredSignatureError:
        return Response({"message": "Refresh token expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except _jwt.InvalidTokenError:
        return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)