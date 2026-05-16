"""Unit tests for application services with mocked repositories."""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from src.application.dtos import CreatePostRequest, EditPostRequest, RegisterRequest, LoginRequest
from src.application.services.post_service import PostService, ForbiddenError, NotFoundError
from src.application.services.auth_service import AuthService, AuthenticationError, ConflictError
from src.domain.entities.post import Post, PostStatus
from src.domain.entities.user import User
from src.domain.exceptions import DomainException
from src.domain.ports import PostRepository, LikeRepository, UserRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from datetime import datetime


def make_user(username="testuser", email="test@example.com"):
    return User(
        id=uuid4(),
        username=Username(username),
        email=Email(email),
        password_hash="hashed",
        bio="",
        avatar_url=None,
        is_active=True,
        created_at=datetime.utcnow(),
    )


def make_post(author_id=None, content="Test post"):
    return Post.create(author_id=author_id or uuid4(), content=content)


# ── PostService tests ──────────────────────────────────────────────────────────

class TestPostService:
    def setup_method(self):
        self.mock_posts = Mock(spec=PostRepository)
        self.mock_likes = Mock(spec=LikeRepository)
        self.mock_users = Mock(spec=UserRepository)
        self.svc = PostService(self.mock_posts, self.mock_likes, self.mock_users)

    def test_create_post_saves_and_returns_response(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.mock_posts.save.return_value = post
        self.mock_users.find_by_id.return_value = user

        result = self.svc.create_post(user.id, CreatePostRequest(content="Hello!"))

        self.mock_posts.save.assert_called_once()
        assert result.content == "Hello!"
        assert result.author_username == "testuser"

    def test_delete_own_post_succeeds(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.mock_posts.find_by_id.return_value = post
        self.mock_posts.save.return_value = post

        self.svc.delete_post(user_id=user.id, post_id=post.id)

        self.mock_posts.save.assert_called_once()

    def test_delete_other_users_post_raises_forbidden(self):
        author = make_user()
        attacker = make_user(username="attacker", email="a@a.com")
        post = make_post(author_id=author.id)
        self.mock_posts.find_by_id.return_value = post

        with pytest.raises(ForbiddenError):
            self.svc.delete_post(user_id=attacker.id, post_id=post.id)

    def test_like_post_increments_count(self):
        user = make_user()
        post = make_post(author_id=uuid4())
        self.mock_posts.find_by_id.return_value = post
        self.mock_likes.has_liked.return_value = False
        self.mock_posts.save.return_value = post

        self.svc.like_post(user_id=user.id, post_id=post.id)

        self.mock_likes.like.assert_called_once_with(user.id, post.id)
        assert post.like_count == 1

    def test_double_like_raises_domain_exception(self):
        user = make_user()
        post = make_post()
        self.mock_posts.find_by_id.return_value = post
        self.mock_likes.has_liked.return_value = True

        with pytest.raises(DomainException):
            self.svc.like_post(user_id=user.id, post_id=post.id)

    def test_get_nonexistent_post_raises_not_found(self):
        self.mock_posts.find_by_id.return_value = None

        with pytest.raises(NotFoundError):
            self.svc._get_or_raise(uuid4())


# ── AuthService tests ──────────────────────────────────────────────────────────

class TestAuthService:
    def setup_method(self):
        self.mock_users = Mock(spec=UserRepository)
        self.mock_pw = Mock()
        self.mock_jwt = Mock()
        self.mock_notify = Mock()
        self.svc = AuthService(self.mock_users, self.mock_pw, self.mock_jwt, self.mock_notify)

    def test_register_creates_user_and_returns_tokens(self):
        self.mock_users.exists_by_email.return_value = False
        self.mock_users.exists_by_username.return_value = False
        self.mock_pw.hash.return_value = "bcrypt_hash"
        self.mock_users.save.return_value = make_user()
        self.mock_jwt.create_tokens.return_value = Mock(access_token="acc", refresh_token="ref")

        result = self.svc.register(RegisterRequest(username="newuser", email="new@test.com", password="password123"))

        self.mock_users.save.assert_called_once()
        self.mock_notify.send_welcome.assert_called_once()

    def test_register_duplicate_email_raises_conflict(self):
        self.mock_users.exists_by_email.return_value = True

        with pytest.raises(ConflictError):
            self.svc.register(RegisterRequest(username="u", email="taken@test.com", password="pass12345"))

    def test_login_wrong_password_raises_auth_error(self):
        user = make_user()
        self.mock_users.find_by_email.return_value = user
        self.mock_pw.verify.return_value = False

        with pytest.raises(AuthenticationError):
            self.svc.login(LoginRequest(email="test@example.com", password="wrong"))

    def test_login_inactive_user_raises_auth_error(self):
        user = make_user()
        user.is_active = False
        self.mock_users.find_by_email.return_value = user
        self.mock_pw.verify.return_value = True

        with pytest.raises(AuthenticationError):
            self.svc.login(LoginRequest(email="test@example.com", password="correct"))
