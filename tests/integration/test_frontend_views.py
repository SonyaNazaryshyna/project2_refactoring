"""Integration tests — Frontend Views."""
import pytest
from django.test import Client


def make_jwt_token(user_id, username, is_admin=False):
    """Create a real JWT token for testing."""
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


@pytest.mark.django_db
class TestAuthViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_login_view_get(self):
        response = self.client.get("/login")
        assert response.status_code == 200

    def test_login_view_redirects_if_logged_in(self):
        from src.infrastructure.database.models import UserORM
        user = UserORM.objects.create_user(username="u1", email="u1@test.com", password="pw")
        token = make_jwt_token(user.id, user.username)
        self.client.cookies["access_token"] = token
        response = self.client.get("/login")
        assert response.status_code == 302

    def test_login_view_post_success(self):
        from src.infrastructure.database.models import UserORM
        UserORM.objects.create_user(username="loginuser", email="login@test.com", password="password123")
        response = self.client.post("/login", {"email": "login@test.com", "password": "password123"})
        assert response.status_code == 302

    def test_login_view_post_wrong_password(self):
        from src.infrastructure.database.models import UserORM
        UserORM.objects.create_user(username="loginuser2", email="login2@test.com", password="password123")
        response = self.client.post("/login", {"email": "login2@test.com", "password": "wrong"})
        assert response.status_code == 200

    def test_register_view_get(self):
        response = self.client.get("/register")
        assert response.status_code == 200

    def test_register_view_post_success(self):
        response = self.client.post("/register", {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
            "bio": "",
        })
        assert response.status_code == 302

    def test_register_view_post_duplicate(self):
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
        assert response.status_code == 200

    def test_logout_view(self):
        response = self.client.get("/logout")
        assert response.status_code == 302

    def test_register_redirects_if_logged_in(self):
        from src.infrastructure.database.models import UserORM
        user = UserORM.objects.create_user(username="ru", email="ru@test.com", password="pw")
        token = make_jwt_token(user.id, user.username)
        self.client.cookies["access_token"] = token
        response = self.client.get("/register")
        assert response.status_code == 302


@pytest.mark.django_db
class TestFeedViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        from src.infrastructure.database.models import UserORM
        self.user = UserORM.objects.create_user(
            username="feeduser", email="feed@test.com", password="password123"
        )
        self.token = make_jwt_token(self.user.id, self.user.username)
        self.client.cookies["access_token"] = self.token

    def test_feed_view_authenticated(self):
        response = self.client.get("/")
        assert response.status_code == 200

    def test_feed_view_unauthenticated(self):
        client = Client()
        response = client.get("/")
        assert response.status_code == 302

    def test_explore_view_authenticated(self):
        response = self.client.get("/explore")
        assert response.status_code == 200

    def test_explore_view_unauthenticated(self):
        client = Client()
        response = client.get("/explore")
        assert response.status_code == 302

    def test_search_view_authenticated(self):
        response = self.client.get("/search")
        assert response.status_code == 200

    def test_search_view_with_query(self):
        response = self.client.get("/search?q=feed")
        assert response.status_code == 200

    def test_search_view_unauthenticated(self):
        client = Client()
        response = client.get("/search")
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        from src.infrastructure.database.models import UserORM
        self.user = UserORM.objects.create_user(
            username="profileuser", email="profile@test.com", password="password123"
        )
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
        client = Client()
        response = client.post(f"/user/{self.user.username}/update", {"bio": "new bio"})
        assert response.status_code == 302

    def test_update_profile_get_redirects(self):
        response = self.client.get(f"/user/{self.user.username}/update")
        assert response.status_code == 302

    def test_update_profile_post_success(self):
        response = self.client.post(f"/user/{self.user.username}/update", {
            "username": self.user.username,
            "bio": "updated bio",
        })
        assert response.status_code == 302


@pytest.mark.django_db
class TestAdminViews:
    def setup_method(self):
        self.client = Client(enforce_csrf_checks=False)
        from src.infrastructure.database.models import UserORM
        self.admin = UserORM.objects.create_user(
            username="adminuser", email="admin@test.com", password="password123"
        )
        self.admin.role = "ROLE_ADMIN"
        self.admin.save()
        self.token = make_jwt_token(self.admin.id, self.admin.username, is_admin=True)
        self.client.cookies["access_token"] = self.token

        self.target = UserORM.objects.create_user(
            username="targetuser", email="target@test.com", password="password123"
        )

    def test_admin_panel_view(self):
        response = self.client.get("/admin-panel")
        assert response.status_code == 200

    def test_admin_panel_non_admin_redirects(self):
        client = Client(enforce_csrf_checks=False)
        from src.infrastructure.database.models import UserORM
        user = UserORM.objects.create_user(username="regular", email="regular@test.com", password="pw")
        token = make_jwt_token(user.id, user.username)
        client.cookies["access_token"] = token
        response = client.get("/admin-panel")
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

    def test_admin_delete_view(self):
        from src.infrastructure.database.models import UserORM
        to_delete = UserORM.objects.create_user(
            username="todelete", email="todelete@test.com", password="pw"
        )
        response = self.client.post(f"/admin-panel/delete/{to_delete.username}")
        assert response.status_code == 302
        assert not UserORM.objects.filter(username="todelete").exists()

    def test_admin_cannot_delete_self(self):
        response = self.client.post(f"/admin-panel/delete/{self.admin.username}")
        assert response.status_code == 302
        from src.infrastructure.database.models import UserORM
        assert UserORM.objects.filter(username="adminuser").exists()