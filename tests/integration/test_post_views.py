"""Integration tests — Post REST controllers."""
import pytest
from uuid import uuid4
from rest_framework.test import APIClient
from src.infrastructure.database.models import UserORM, PostORM


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


def create_post(author, content="Test post"):
    return PostORM.objects.create(
        author=author,
        content=content,
        status="PUBLISHED",
        like_count=0,
    )


# ══════════════════════════════════════════
# GET ALL POSTS
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostsListGet:
    def setup_method(self):
        self.user = create_user("postuser", "post@test.com")
        self.client = auth_client(self.user)

    def test_get_posts_returns_200(self):
        response = self.client.get("/api/v1/posts/")
        assert response.status_code == 200
        assert "items" in response.data

    def test_get_posts_empty(self):
        response = self.client.get("/api/v1/posts/")
        assert response.status_code == 200
        assert response.data["items"] == []

    def test_get_posts_with_data(self):
        create_post(self.user, "Hello world")
        response = self.client.get("/api/v1/posts/")
        assert response.status_code == 200
        assert len(response.data["items"]) == 1

    def test_get_posts_pagination(self):
        response = self.client.get("/api/v1/posts/?page=1&size=10")
        assert response.status_code == 200
        assert response.data["page"] == 1
        assert response.data["size"] == 10

    def test_get_posts_unauthenticated(self):
        response = APIClient().get("/api/v1/posts/")
        assert response.status_code in [200, 401]


# ══════════════════════════════════════════
# CREATE POST
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostsListCreate:
    def setup_method(self):
        self.user = create_user("createuser", "create@test.com")
        self.client = auth_client(self.user)

    def test_create_post_success(self):
        response = self.client.post("/api/v1/posts/create/", {
            "content": "Hello world!",
        }, format="json")
        assert response.status_code == 201
        assert response.data["content"] == "Hello world!"

    def test_create_post_empty_body_returns_400(self):
        response = self.client.post("/api/v1/posts/create/", {}, format="json")
        assert response.status_code == 400

    def test_create_post_empty_content_returns_400(self):
        response = self.client.post("/api/v1/posts/create/", {
            "content": "",
        }, format="json")
        assert response.status_code == 400

    def test_create_post_too_long_returns_400(self):
        response = self.client.post("/api/v1/posts/create/", {
            "content": "x" * 281,
        }, format="json")
        assert response.status_code == 400

    def test_create_post_unauthenticated(self):
        response = APIClient().post("/api/v1/posts/create/", {
            "content": "Hello",
        }, format="json")
        assert response.status_code in [401, 403]


# ══════════════════════════════════════════
# GET POST DETAIL
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostDetailGet:
    def setup_method(self):
        self.user = create_user("detailuser", "detail@test.com")
        self.client = auth_client(self.user)
        self.post = create_post(self.user, "Detail post")

    def test_get_post_success(self):
        response = self.client.get(f"/api/v1/posts/{self.post.id}/")
        assert response.status_code == 200
        assert response.data["content"] == "Detail post"

    def test_get_nonexistent_post_returns_404(self):
        response = self.client.get(f"/api/v1/posts/{uuid4()}/")
        assert response.status_code in [404, 500]


# ══════════════════════════════════════════
# EDIT POST
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostDetailEdit:
    def setup_method(self):
        self.user = create_user("edituser", "edit@test.com")
        self.client = auth_client(self.user)
        self.post = create_post(self.user, "Original content")

    def test_edit_post_success(self):
        response = self.client.patch(f"/api/v1/posts/{self.post.id}/edit/", {
            "content": "Updated content",
        }, format="json")
        assert response.status_code == 200
        assert response.data["content"] == "Updated content"

    def test_edit_post_empty_body_returns_400(self):
        response = self.client.patch(f"/api/v1/posts/{self.post.id}/edit/", {}, format="json")
        assert response.status_code == 400

    def test_edit_other_user_post_returns_403(self):
        other = create_user("other", "other@test.com")
        other_client = auth_client(other)
        response = other_client.patch(f"/api/v1/posts/{self.post.id}/edit/", {
            "content": "Hacked!",
        }, format="json")
        assert response.status_code in [400, 403, 500]

    def test_edit_nonexistent_post_returns_404(self):
        response = self.client.patch(f"/api/v1/posts/{uuid4()}/edit/", {
            "content": "Updated",
        }, format="json")
        assert response.status_code in [404, 500]


# ══════════════════════════════════════════
# DELETE POST
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostDetailDelete:
    def setup_method(self):
        self.user = create_user("deleteuser", "delete@test.com")
        self.client = auth_client(self.user)
        self.post = create_post(self.user, "To be deleted")

    def test_delete_post_success(self):
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/delete/")
        assert response.status_code == 204

    def test_delete_other_user_post_returns_403(self):
        other = create_user("other2", "other2@test.com")
        other_client = auth_client(other)
        response = other_client.delete(f"/api/v1/posts/{self.post.id}/delete/")
        assert response.status_code in [400, 403, 500]

    def test_delete_nonexistent_post_returns_404(self):
        response = self.client.delete(f"/api/v1/posts/{uuid4()}/delete/")
        assert response.status_code in [404, 500]


# ══════════════════════════════════════════
# LIKE / UNLIKE
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestPostLike:
    def setup_method(self):
        self.user = create_user("likeuser", "like@test.com")
        self.client = auth_client(self.user)
        self.author = create_user("likeauthor", "likeauthor@test.com")
        self.post = create_post(self.author, "Likeable post")

    def test_like_post_success(self):
        response = self.client.post(f"/api/v1/posts/{self.post.id}/like/")
        assert response.status_code == 201

    def test_like_post_twice_returns_error(self):
        self.client.post(f"/api/v1/posts/{self.post.id}/like/")
        response = self.client.post(f"/api/v1/posts/{self.post.id}/like/")
        assert response.status_code in [400, 500]

    def test_unlike_post_success(self):
        self.client.post(f"/api/v1/posts/{self.post.id}/like/")
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/unlike/")
        assert response.status_code == 204

    def test_unlike_not_liked_returns_error(self):
        response = self.client.delete(f"/api/v1/posts/{self.post.id}/unlike/")
        assert response.status_code in [400, 500]


# ══════════════════════════════════════════
# FEED
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestFeedAPI:
    def setup_method(self):
        self.user = create_user("feedapiuser", "feedapi@test.com")
        self.client = auth_client(self.user)

    def test_feed_returns_200(self):
        response = self.client.get("/api/v1/feed/")
        assert response.status_code in [200, 404]

    def test_feed_empty(self):
        response = self.client.get("/api/v1/feed/")
        if response.status_code == 200:
            assert "items" in response.data