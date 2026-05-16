"""Integration tests — Dependency Injection Container."""
import pytest
from unittest.mock import patch


@pytest.mark.django_db
class TestContainer:
    def test_get_jwt_provider_returns_instance(self):
        from src.presentation.config.container import get_jwt_provider
        from src.infrastructure.security.jwt_provider import JWTProvider

        get_jwt_provider.cache_clear()
        provider = get_jwt_provider()
        assert isinstance(provider, JWTProvider)

    def test_get_jwt_provider_is_cached(self):
        from src.presentation.config.container import get_jwt_provider

        get_jwt_provider.cache_clear()
        p1 = get_jwt_provider()
        p2 = get_jwt_provider()
        assert p1 is p2

    def test_get_auth_service_returns_instance(self):
        from src.presentation.config.container import get_auth_service
        from src.application.services.auth_service import AuthService

        svc = get_auth_service()
        assert isinstance(svc, AuthService)

    def test_get_post_service_returns_instance(self):
        from src.presentation.config.container import get_post_service
        from src.application.services.post_service import PostService

        svc = get_post_service()
        assert isinstance(svc, PostService)

    def test_get_user_service_returns_instance(self):
        from src.presentation.config.container import get_user_service
        from src.application.services.user_service import UserService

        svc = get_user_service()
        assert isinstance(svc, UserService)

    def test_get_auth_service_creates_new_each_time(self):
        from src.presentation.config.container import get_auth_service

        s1 = get_auth_service()
        s2 = get_auth_service()
        assert s1 is not s2

    def test_get_post_service_creates_new_each_time(self):
        from src.presentation.config.container import get_post_service

        s1 = get_post_service()
        s2 = get_post_service()
        assert s1 is not s2

    def test_get_user_service_creates_new_each_time(self):
        from src.presentation.config.container import get_user_service

        s1 = get_user_service()
        s2 = get_user_service()
        assert s1 is not s2