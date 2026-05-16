"""Dependency injection container — wires all layers together."""
from __future__ import annotations
from functools import lru_cache
from django.conf import settings

from src.infrastructure.database.repositories import (
    DjangoUserRepository,
    DjangoPostRepository,
    DjangoFollowRepository,
    DjangoLikeRepository,
)
from src.infrastructure.security.jwt_provider import JWTProvider, JWTConfig
from src.infrastructure.security.password import PasswordEncoder
from src.infrastructure.external.notification import CeleryNotificationSender
from src.application.services.auth_service import AuthService
from src.application.services.post_service import PostService
from src.application.services.user_service import UserService


@lru_cache(maxsize=1)
def get_jwt_provider() -> JWTProvider:
    cfg = JWTConfig(
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_seconds=int(settings.JWT_ACCESS_TTL.total_seconds()),
        refresh_ttl_seconds=int(settings.JWT_REFRESH_TTL.total_seconds()),
    )
    return JWTProvider(cfg)


def get_auth_service() -> AuthService:
    return AuthService(
        user_repo=DjangoUserRepository(),
        password_encoder=PasswordEncoder(),
        jwt_provider=get_jwt_provider(),
        notification_sender=CeleryNotificationSender(),
    )


def get_post_service() -> PostService:
    return PostService(
        post_repo=DjangoPostRepository(),
        like_repo=DjangoLikeRepository(),
        user_repo=DjangoUserRepository(),
    )


def get_user_service() -> UserService:
    return UserService(
        user_repo=DjangoUserRepository(),
        follow_repo=DjangoFollowRepository(),
        notification_sender=CeleryNotificationSender(),
    )
