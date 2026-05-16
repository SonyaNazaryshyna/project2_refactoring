"""Integration tests — Frontend and Auth Views."""
import pytest
from django.test import Client
from src.infrastructure.database.models import UserORM


def make_jwt_token(user_id, username, is_admin=False):
    from src.infrastructure.security.jwt_provider import JWTProvider, JWTConfig
    from django.conf import settings

    cfg = JWTConfig(
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )
    provider = JWTProvider(cfg)
    return provider.create_tokens(str(user_id), role="ROLE_ADMIN" if is_admin else "ROLE_USER").access_token


def create_user(username, email, password="password123", role="ROLE_USER", is_active=True):
    return UserORM.objects.create(
        username=username,
        email=email,
        password=password,
        role=role,
        is_active=is_active,
    )


# ══════════════════════════════════════════
# AUTH API VIEWS
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestRegisterAPIView:
    def setup_method(self):
        self.client = Client()

    def test_register_empty_body_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_register_invalid_data_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"username": "u", "email": "notanemail", "password": "123"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_register_success_returns_201(self):
        response = self.client.post(
            "/api/v1/auth/register",
            {"username": "newuser", "email": "new@test.com", "password": "password123"},
            content_type="application/json",
        )
        assert response.status_code == 201
        assert "access_token" in response.json()

    def test_register_duplicate_email_returns_400(self):
        self.client.post(
            "/api/v1/auth/register",
            {"username": "user1", "email": "taken@test.com", "password": "password123"},
            content_type="application/json",
        )
        response = self.client.post(
            "/api/v1/auth/register",
            {"username": "user2", "email": "taken@test.com", "password": "password123"},
            content_type="application/json",
        )
        assert response.status_code in [400, 409]


@pytest.mark.django_db
class TestLoginAPIView:
    def setup_method(self):
        self.client = Client()
        self.client.post(
            "/api/v1/auth/register",
            {"username": "loginuser", "email": "login@test.com", "password": "password123"},
            content_type="application/json",
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "login@test.com", "password": "password123"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "login@test.com", "password": "wrongpassword"},
            content_type="application/json",
        )
        assert response.status_code in [400, 401]

    def test_login_empty_body_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_login_nonexistent_user_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "ghost@test.com", "password": "password123"},
            content_type="application/json",
        )
        assert response.status_code in [400, 401]


@pytest.mark.django_db
class TestRefreshTokenAPIView:
    def setup_method(self):
        self.client = Client()
        reg = self.client.post(
            "/api/v1/auth/register",
            {"username": "refreshuser", "email": "refresh@test.com", "password": "password123"},
            content_type="application/json",
        )
        self.refresh_token = reg.json().get("refresh_token") if reg.status_code == 201 else None

    def test_refresh_success(self):
        if not self.refresh_token:
            pytest.skip("Registration failed")
        response = self.client.post(
            "/api/v1/auth/refresh",
            {"refresh_token": self.refresh_token},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_missing_token_returns_400(self):
        response = self.client.post(
            "/api/v1/auth/refresh",
            {},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_refresh_invalid_token_returns_401(self):
        response = self.client.post(
            "/api/v1/auth/refresh",
            {"refresh_token": "invalid.token.here"},
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_refresh_expired_token_returns_401(self):
        response = self.client.post(
            "/api/v1/auth/refresh",
            {"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwidHlwZSI6InJlZnJlc2giLCJleHAiOjF9.invalid"},
            content_type="application/json",
        )
        assert response.status_code == 401


# ══════════════════════════════════════════
# FRONTEND VIEWS
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestFrontendAuthViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_login_view_get(self):
        response = self.client.get("/login")
        assert response.status_code == 200

    def test_register_view_get(self):
        response = self.client.get("/register")
        assert response.status_code == 200

    def test_login_redirects_if_logged_in(self):
        user = create_user("loggedinuser", "loggedin@test.com")
        token = make_jwt_token(user.id, user.username)
        self.client.cookies["access_token"] = token
        response = self.client.get("/login")
        assert response.status_code == 302

    def test_register_redirects_if_logged_in(self):
        user = create_user("loggedinuser2", "loggedin2@test.com")
        token = make_jwt_token(user.id, user.username)
        self.client.cookies["access_token"] = token
        response = self.client.get("/register")
        assert response.status_code == 302

    def test_login_post_success(self):
        self.client.post("/api/v1/auth/register",
            {"username": "frontlogin", "email": "frontlogin@test.com", "password": "password123"},
            content_type="application/json",
        )
        response = self.client.post("/login", {
            "email": "frontlogin@test.com",
            "password": "password123",
        })
        assert response.status_code == 302

    def test_login_post_wrong_password(self):
        self.client.post("/api/v1/auth/register",
            {"username": "frontlogin2", "email": "frontlogin2@test.com", "password": "password123"},
            content_type="application/json",
        )
        response = self.client.post("/login", {
            "email": "frontlogin2@test.com",
            "password": "wrong",
        })
        assert response.status_code == 200

    def test_register_post_success(self):
        response = self.client.post("/register", {
            "username": "frontreg",
            "email": "frontreg@test.com",
            "password": "password123",
            "bio": "",
        })
        assert response.status_code == 302

    def test_register_post_duplicate(self):
        self.client.post("/register", {
            "username": "dupuser",
            "email": "dup@test.com",
            "password": "password123",
        })
        response = self.client.post("/register", {
            "username": "dupuser",  
            "email": "dup@test.com",
            "password": "password123",
        })
        assert response.status_code in [200, 302]

    def test_logout_view(self):
        response = self.client.get("/logout")
        assert response.status_code == 302


@pytest.mark.django_db
class TestFeedViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = create_user("feeduser", "feed@test.com")
        self.token = make_jwt_token(self.user.id, self.user.username)
        self.client.cookies["access_token"] = self.token

    def test_feed_view_authenticated(self):
        response = self.client.get("/")
        assert response.status_code == 200

    def test_feed_view_unauthenticated(self):
        response = Client().get("/")
        assert response.status_code == 302

    def test_explore_view_authenticated(self):
        response = self.client.get("/explore")
        assert response.status_code == 200

    def test_explore_view_unauthenticated(self):
        response = Client().get("/explore")
        assert response.status_code == 302

    def test_search_view_authenticated(self):
        response = self.client.get("/search")
        assert response.status_code == 200

    def test_search_view_with_query(self):
        response = self.client.get("/search?q=feed")
        assert response.status_code == 200

    def test_search_view_unauthenticated(self):
        response = Client().get("/search")
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = create_user("profileuser", "profile@test.com")
        self.token = make_jwt_token(self.user.id, self.user.username)
        self.client.cookies["access_token"] = self.token

    def test_my_profile_redirects(self):
        response = self.client.get("/profile")
        assert response.status_code == 302

    def test_user_profile_view(self):
        response = self.client.get(f"/user/{self.user.username}")
        assert response.status_code == 200

    def test_user_profile_not_found_redirects(self):
        response = self.client.get("/user/ghostuser")
        assert response.status_code == 302

    def test_followers_view(self):
        response = self.client.get(f"/user/{self.user.username}/followers")
        assert response.status_code == 200

    def test_following_view(self):
        response = self.client.get(f"/user/{self.user.username}/following")
        assert response.status_code == 200

    def test_followers_not_found_redirects(self):
        response = self.client.get("/user/ghost/followers")
        assert response.status_code == 302

    def test_update_profile_unauthenticated(self):
        response = Client().get(f"/user/{self.user.username}/edit")
        assert response.status_code == 302

    def test_update_profile_get_redirects(self):
        response = self.client.get(f"/user/{self.user.username}/edit")
        assert response.status_code == 302

    def test_update_profile_post_success(self):
        response = self.client.post(f"/user/{self.user.username}/edit", {
            "username": self.user.username,
            "bio": "updated bio",
        })
        assert response.status_code == 302


@pytest.mark.django_db
class TestAdminViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        self.admin = create_user("adminuser", "admin@test.com", role="ROLE_ADMIN")
        self.token = make_jwt_token(self.admin.id, self.admin.username, is_admin=True)
        self.client.cookies["access_token"] = self.token
        self.target = create_user("targetuser", "target@test.com")

    def test_admin_panel_view(self):
        response = self.client.get("/admin-panel")
        assert response.status_code == 200

    def test_admin_panel_non_admin_redirects(self):
        client = Client(enforce_csrf_checks=False)
        user = create_user("regular", "regular@test.com")
        token = make_jwt_token(user.id, user.username)
        client.cookies["access_token"] = token
        response = client.get("/admin-panel")
        assert response.status_code == 302

    def test_admin_panel_unauthenticated_redirects(self):
        response = Client().get("/admin-panel")
        assert response.status_code == 302

    def test_admin_ban_view(self):
        response = self.client.post(f"/admin-panel/ban/{self.target.username}")
        assert response.status_code == 302
        self.target.refresh_from_db()
        assert self.target.is_active is False

    def test_admin_unban_view(self):
        self.target.is_active = False
        self.target.save()
        response = self.client.post(f"/admin-panel/unban/{self.target.username}")
        assert response.status_code == 302
        self.target.refresh_from_db()
        assert self.target.is_active is True

    def test_admin_cannot_delete_self(self):
        response = self.client.post(f"/admin-panel/delete/{self.admin.username}")
        assert response.status_code == 302
        assert UserORM.objects.filter(username="adminuser").exists()