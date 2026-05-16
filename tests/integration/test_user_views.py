"""Integration tests — User REST controllers."""
import pytest
from rest_framework.test import APIClient
from src.infrastructure.database.models import UserORM


def create_user(username, email, role="ROLE_USER"):
    return UserORM.objects.create(
        username=username,
        email=email,
        password="hashed",
        is_active=True,
        role=role,
    )


def get_token(user_id, role="ROLE_USER"):
    from src.infrastructure.security.jwt_provider import JWTProvider, JWTConfig
    from django.conf import settings
    cfg = JWTConfig(
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_seconds=3600,
        refresh_ttl_seconds=86400,
    )
    return JWTProvider(cfg).create_tokens(str(user_id), role=role).access_token


def auth_client(user):
    client = APIClient()
    token = get_token(user.id)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# ══════════════════════════════════════════
# ME
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestMeView:
    def setup_method(self):
        self.user = create_user("meuser", "me@test.com")
        self.client = auth_client(self.user)

    def test_get_me_success(self):
        response = self.client.get("/api/v1/users/me")
        assert response.status_code == 200
        assert response.data["username"] == "meuser"

    def test_get_me_unauthenticated(self):
        response = APIClient().get("/api/v1/users/me")
        assert response.status_code in [401, 403]

    def test_update_me_success(self):
        response = self.client.patch("/api/v1/users/me/update", {
            "bio": "Updated bio",
        }, format="json")
        assert response.status_code == 200
        assert response.data["bio"] == "Updated bio"

    def test_update_me_unauthenticated(self):
        response = APIClient().patch("/api/v1/users/me/update", {
            "bio": "bio",
        }, format="json")
        assert response.status_code in [401, 403]

    def test_update_me_empty_body(self):
        response = self.client.patch("/api/v1/users/me/update", {}, format="json")
        assert response.status_code in [200, 400]


# ══════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestUserProfileView:
    def setup_method(self):
        self.user = create_user("profileuser", "profile@test.com")
        self.client = auth_client(self.user)

    def test_get_profile_success(self):
        response = self.client.get(f"/api/v1/users/{self.user.username}")
        assert response.status_code == 200
        assert response.data["username"] == "profileuser"

    def test_get_profile_unauthenticated(self):
        response = APIClient().get(f"/api/v1/users/{self.user.username}")
        assert response.status_code == 200

    def test_get_profile_not_found(self):
        response = self.client.get("/api/v1/users/ghostuser")
        assert response.status_code in [404, 500]


# ══════════════════════════════════════════
# FOLLOW / UNFOLLOW
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestFollowView:
    def setup_method(self):
        self.user = create_user("follower", "follower@test.com")
        self.target = create_user("target", "target@test.com")
        self.client = auth_client(self.user)

    def test_follow_user_success(self):
        response = self.client.post(f"/api/v1/users/{self.target.username}/follow")
        assert response.status_code == 201

    def test_follow_yourself_returns_error(self):
        response = self.client.post(f"/api/v1/users/{self.user.username}/follow")
        assert response.status_code in [400, 422, 500]

    def test_follow_twice_returns_error(self):
        self.client.post(f"/api/v1/users/{self.target.username}/follow")
        response = self.client.post(f"/api/v1/users/{self.target.username}/follow")
        assert response.status_code in [400, 422, 500]

    def test_unfollow_success(self):
        self.client.post(f"/api/v1/users/{self.target.username}/follow")
        response = self.client.delete(f"/api/v1/users/{self.target.username}/follow")
        assert response.status_code == 204

    def test_unfollow_not_following_returns_error(self):
        response = self.client.delete(f"/api/v1/users/{self.target.username}/follow")
        assert response.status_code in [400, 422, 500]

    def test_follow_unauthenticated(self):
        response = APIClient().post(f"/api/v1/users/{self.target.username}/follow")
        assert response.status_code in [401, 403]


# ══════════════════════════════════════════
# FOLLOWERS / FOLLOWING
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestFollowersFollowingView:
    def setup_method(self):
        self.user = create_user("listuser", "list@test.com")
        self.other = create_user("listother", "listother@test.com")
        self.client = auth_client(self.user)

    def test_get_followers_success(self):
        response = self.client.get(f"/api/v1/users/{self.user.username}/followers")
        assert response.status_code == 200

    def test_get_followers_unauthenticated(self):
        response = APIClient().get(f"/api/v1/users/{self.user.username}/followers")
        assert response.status_code == 200

    def test_get_followers_not_found(self):
        response = self.client.get("/api/v1/users/ghost/followers")
        assert response.status_code in [404, 500]

    def test_get_following_success(self):
        response = self.client.get(f"/api/v1/users/{self.user.username}/following")
        assert response.status_code == 200

    def test_get_following_unauthenticated(self):
        response = APIClient().get(f"/api/v1/users/{self.user.username}/following")
        assert response.status_code == 200

    def test_get_following_not_found(self):
        response = self.client.get("/api/v1/users/ghost/following")
        assert response.status_code in [404, 500]

    def test_followers_after_follow(self):
        other_client = auth_client(self.other)
        other_client.post(f"/api/v1/users/{self.user.username}/follow")
        response = self.client.get(f"/api/v1/users/{self.user.username}/followers")
        assert response.status_code == 200
        assert response.data["total"] >= 1

    def test_following_after_follow(self):
        self.client.post(f"/api/v1/users/{self.other.username}/follow")
        response = self.client.get(f"/api/v1/users/{self.user.username}/following")
        assert response.status_code == 200
        assert response.data["total"] >= 1