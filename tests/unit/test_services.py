"""Unit tests — Application Services."""
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime

from src.application.dtos import (
    CreatePostRequest, EditPostRequest,
    RegisterRequest, LoginRequest,
)
from src.application.services.post_service import (
    PostService, ForbiddenError, NotFoundError,
)
from src.application.services.auth_service import (
    AuthService, AuthenticationError, ConflictError,
)
from src.application.services.user_service import UserService
from src.domain.entities.post import Post, PostStatus
from src.domain.entities.user import User
from src.domain.exceptions import DomainException
from src.domain.ports import PostRepository, LikeRepository, UserRepository, FollowRepository, NotificationSender
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from src.application.services.auth_service import AuthService, AuthenticationError, ConflictError


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_user(username="testuser", email="test@example.com", active=True):
    u = User(
        id=uuid4(), username=Username(username), email=Email(email),
        password_hash="hashed_pw", bio="", avatar_url=None,
        is_active=active, created_at=datetime.utcnow(),
    )
    return u


def make_post(author_id=None, content="Test post", status=PostStatus.PUBLISHED):
    p = Post.create(author_id=author_id or uuid4(), content=content)
    p.status = status
    return p


# ══════════════════════════════════════════
# AUTH SERVICE
# ══════════════════════════════════════════

class TestAuthServiceRegister:
    def setup_method(self):
        self.users = Mock(spec=UserRepository)
        self.pw = Mock()
        self.jwt = Mock()
        self.notify = Mock(spec=NotificationSender)
        self.svc = AuthService(self.users, self.pw, self.jwt, self.notify)

    def test_register_success(self):
        self.users.exists_by_email.return_value = False
        self.users.exists_by_username.return_value = False
        self.pw.hash.return_value = "bcrypt_hash"
        self.users.save.return_value = make_user()
        self.jwt.create_tokens.return_value = Mock(access_token="acc", refresh_token="ref")

        result = self.svc.register(RegisterRequest(
            username="newuser", email="new@test.com", password="password123"
        ))

        self.users.save.assert_called_once()
        self.notify.send_welcome.assert_called_once()
        assert result.access_token == "acc"

    def test_register_duplicate_email_raises(self):
        self.users.exists_by_email.return_value = True
        with pytest.raises(ConflictError, match="Email"):
            self.svc.register(RegisterRequest(
                username="user", email="taken@test.com", password="password123"
            ))

    def test_register_duplicate_username_raises(self):
        self.users.exists_by_email.return_value = False
        self.users.exists_by_username.return_value = True
        with pytest.raises(ConflictError, match="Username"):
            self.svc.register(RegisterRequest(
                username="taken", email="new@test.com", password="password123"
            ))

    def test_register_hashes_password(self):
        self.users.exists_by_email.return_value = False
        self.users.exists_by_username.return_value = False
        self.pw.hash.return_value = "bcrypt_hash"
        self.users.save.return_value = make_user()
        self.jwt.create_tokens.return_value = Mock(access_token="a", refresh_token="r")

        self.svc.register(RegisterRequest(
            username="user", email="u@test.com", password="password123"
        ))

        self.pw.hash.assert_called_once_with("password123")

    def test_register_sends_welcome_notification(self):
        self.users.exists_by_email.return_value = False
        self.users.exists_by_username.return_value = False
        self.pw.hash.return_value = "h"
        saved_user = make_user()
        self.users.save.return_value = saved_user
        self.jwt.create_tokens.return_value = Mock(access_token="a", refresh_token="r")

        self.svc.register(RegisterRequest(
            username="user", email="u@test.com", password="password123"
        ))

        self.notify.send_welcome.assert_called_once()

    def test_register_creates_jwt_tokens(self):
        self.users.exists_by_email.return_value = False
        self.users.exists_by_username.return_value = False
        self.pw.hash.return_value = "h"
        self.users.save.return_value = make_user()
        self.jwt.create_tokens.return_value = Mock(access_token="tok", refresh_token="ref")

        self.svc.register(RegisterRequest(
            username="user", email="u@test.com", password="password123"
        ))

        self.jwt.create_tokens.assert_called_once()
        args, kwargs = self.jwt.create_tokens.call_args
        assert kwargs.get("role") == "ROLE_USER"


class TestAuthServiceLogin:
    def setup_method(self):
        self.users = Mock(spec=UserRepository)
        self.pw = Mock()
        self.jwt = Mock()
        self.notify = Mock(spec=NotificationSender)
        self.svc = AuthService(self.users, self.pw, self.jwt, self.notify)

    def test_login_success(self):
        user = make_user()
        self.users.find_by_email.return_value = user
        self.pw.verify.return_value = True
        self.jwt.create_tokens.return_value = Mock(access_token="acc", refresh_token="ref")

        result = self.svc.login(LoginRequest(email="test@example.com", password="correct"))
        assert result.access_token == "acc"

    def test_login_wrong_password_raises(self):
        user = make_user()
        self.users.find_by_email.return_value = user
        self.pw.verify.return_value = False

        with pytest.raises(AuthenticationError):
            self.svc.login(LoginRequest(email="test@example.com", password="wrong"))

    def test_login_user_not_found_raises(self):
        self.users.find_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            self.svc.login(LoginRequest(email="ghost@test.com", password="pw"))

    def test_login_inactive_user_raises(self):
        user = make_user(active=False)
        self.users.find_by_email.return_value = user
        self.pw.verify.return_value = True

        with pytest.raises(AuthenticationError, match="deactivated"):
            self.svc.login(LoginRequest(email="test@example.com", password="pw"))

    def test_login_verifies_password(self):
        user = make_user()
        self.users.find_by_email.return_value = user
        self.pw.verify.return_value = True
        self.jwt.create_tokens.return_value = Mock(access_token="a", refresh_token="r")

        self.svc.login(LoginRequest(email="test@example.com", password="mypassword"))
        self.pw.verify.assert_called_once_with("mypassword", user.password_hash)


# ══════════════════════════════════════════
# POST SERVICE
# ══════════════════════════════════════════

class TestPostServiceCreate:
    def setup_method(self):
        self.posts = Mock(spec=PostRepository)
        self.likes = Mock(spec=LikeRepository)
        self.users = Mock(spec=UserRepository)
        self.svc = PostService(self.posts, self.likes, self.users)

    def test_create_post_success(self):
        user = make_user()
        post = make_post(author_id=user.id, content="Hello!")
        self.posts.save.return_value = post
        self.users.find_by_id.return_value = user

        result = self.svc.create_post(user.id, CreatePostRequest(content="Hello!"))

        self.posts.save.assert_called_once()
        assert result.content == "Hello!"
        assert result.author_username == "testuser"

    def test_create_post_stores_author_id(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.posts.save.return_value = post
        self.users.find_by_id.return_value = user

        result = self.svc.create_post(user.id, CreatePostRequest(content="Hi"))
        assert result.author_id == user.id

    def test_create_post_not_liked_by_default(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.posts.save.return_value = post
        self.users.find_by_id.return_value = user

        result = self.svc.create_post(user.id, CreatePostRequest(content="Hi"))
        assert result.is_liked_by_me is False


class TestPostServiceDelete:
    def setup_method(self):
        self.posts = Mock(spec=PostRepository)
        self.likes = Mock(spec=LikeRepository)
        self.users = Mock(spec=UserRepository)
        self.svc = PostService(self.posts, self.likes, self.users)

    def test_delete_own_post(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.posts.find_by_id.return_value = post
        self.posts.save.return_value = post

        self.svc.delete_post(user.id, post.id)
        self.posts.save.assert_called_once()

    def test_delete_other_user_post_raises(self):
        owner = make_user()
        attacker = make_user(username="attacker", email="a@a.com")
        post = make_post(author_id=owner.id)
        self.posts.find_by_id.return_value = post

        with pytest.raises(ForbiddenError):
            self.svc.delete_post(attacker.id, post.id)

    def test_delete_nonexistent_raises(self):
        self.posts.find_by_id.return_value = None

        with pytest.raises(NotFoundError):
            self.svc.delete_post(uuid4(), uuid4())


class TestPostServiceLike:
    def setup_method(self):
        self.posts = Mock(spec=PostRepository)
        self.likes = Mock(spec=LikeRepository)
        self.users = Mock(spec=UserRepository)
        self.svc = PostService(self.posts, self.likes, self.users)

    def test_like_post_success(self):
        user = make_user()
        post = make_post()
        self.posts.find_by_id.return_value = post
        self.likes.has_liked.return_value = False
        self.posts.save.return_value = post

        self.svc.like_post(user.id, post.id)

        self.likes.like.assert_called_once_with(user.id, post.id)
        assert post.like_count == 1

    def test_like_post_twice_raises(self):
        user = make_user()
        post = make_post()
        self.posts.find_by_id.return_value = post
        self.likes.has_liked.return_value = True

        with pytest.raises(DomainException):
            self.svc.like_post(user.id, post.id)

    def test_unlike_post_success(self):
        user = make_user()
        post = make_post()
        post.increment_likes()
        self.posts.find_by_id.return_value = post
        self.likes.has_liked.return_value = True
        self.posts.save.return_value = post

        self.svc.unlike_post(user.id, post.id)

        self.likes.unlike.assert_called_once_with(user.id, post.id)
        assert post.like_count == 0

    def test_unlike_not_liked_raises(self):
        user = make_user()
        post = make_post()
        self.posts.find_by_id.return_value = post
        self.likes.has_liked.return_value = False

        with pytest.raises(DomainException):
            self.svc.unlike_post(user.id, post.id)

    def test_like_nonexistent_post_raises(self):
        self.posts.find_by_id.return_value = None

        with pytest.raises(NotFoundError):
            self.svc.like_post(uuid4(), uuid4())


class TestPostServiceEdit:
    def setup_method(self):
        self.posts = Mock(spec=PostRepository)
        self.likes = Mock(spec=LikeRepository)
        self.users = Mock(spec=UserRepository)
        self.svc = PostService(self.posts, self.likes, self.users)

    def test_edit_own_post(self):
        user = make_user()
        post = make_post(author_id=user.id)
        self.posts.find_by_id.return_value = post
        self.posts.save.return_value = post
        self.users.find_by_id.return_value = user
        self.likes.has_liked.return_value = False

        result = self.svc.edit_post(user.id, post.id, EditPostRequest(content="Edited!"))
        assert result.content == "Edited!"

    def test_edit_other_user_post_raises(self):
        owner = make_user()
        other = make_user(username="other", email="o@o.com")
        post = make_post(author_id=owner.id)
        self.posts.find_by_id.return_value = post

        with pytest.raises(ForbiddenError):
            self.svc.edit_post(other.id, post.id, EditPostRequest(content="Hack!"))

    def test_edit_nonexistent_post_raises(self):
        self.posts.find_by_id.return_value = None

        with pytest.raises(NotFoundError):
            self.svc.edit_post(uuid4(), uuid4(), EditPostRequest(content="x"))


class TestPostServiceFeed:
    def setup_method(self):
        self.posts = Mock(spec=PostRepository)
        self.likes = Mock(spec=LikeRepository)
        self.users = Mock(spec=UserRepository)
        self.svc = PostService(self.posts, self.likes, self.users)

    def test_get_feed_returns_paginated(self):
        user = make_user()
        author = make_user(username="author", email="a@a.com")
        post = make_post(author_id=author.id)
        self.posts.find_feed.return_value = [post]
        self.users.find_by_id.return_value = author
        self.likes.has_liked.return_value = False

        result = self.svc.get_feed(user.id, page=1, size=20)
        assert len(result.items) == 1
        assert result.page == 1

    def test_get_feed_empty(self):
        self.posts.find_feed.return_value = []

        result = self.svc.get_feed(uuid4(), page=1, size=20)
        assert result.items == []


# ══════════════════════════════════════════
# USER SERVICE
# ══════════════════════════════════════════

class TestUserService:
    def setup_method(self):
        self.users = Mock(spec=UserRepository)
        self.follows = Mock(spec=FollowRepository)
        self.notify = Mock(spec=NotificationSender)
        self.svc = UserService(self.users, self.follows, self.notify)

    def test_get_profile_success(self):
        user = make_user()
        self.users.find_by_username.return_value = user

        result = self.svc.get_profile("testuser")
        assert result.username == "testuser"

    def test_get_profile_not_found_raises(self):
        self.users.find_by_username.return_value = None

        with pytest.raises(Exception):
            self.svc.get_profile("ghost")

    def test_follow_success(self):
        follower = make_user()
        target = make_user(username="target", email="t@t.com")
        self.users.find_by_username.return_value = target
        self.users.find_by_id.return_value = follower
        self.follows.is_following.return_value = False

        self.svc.follow(follower.id, "target")
        self.follows.follow.assert_called_once_with(follower.id, target.id)

    def test_follow_yourself_raises(self):
        user = make_user()
        self.users.find_by_username.return_value = user

        with pytest.raises(DomainException):
            self.svc.follow(user.id, "testuser")

    def test_follow_already_following_raises(self):
        follower = make_user()
        target = make_user(username="target", email="t@t.com")
        self.users.find_by_username.return_value = target
        self.follows.is_following.return_value = True

        with pytest.raises(DomainException):
            self.svc.follow(follower.id, "target")

    def test_unfollow_success(self):
        follower = make_user()
        target = make_user(username="target", email="t@t.com")
        self.users.find_by_username.return_value = target
        self.follows.is_following.return_value = True

        self.svc.unfollow(follower.id, "target")
        self.follows.unfollow.assert_called_once_with(follower.id, target.id)

    def test_unfollow_not_following_raises(self):
        follower = make_user()
        target = make_user(username="target", email="t@t.com")
        self.users.find_by_username.return_value = target
        self.follows.is_following.return_value = False

        with pytest.raises(DomainException):
            self.svc.unfollow(follower.id, "target")

    def test_unfollow_not_found_raises(self):
        self.users.find_by_username.return_value = None

        with pytest.raises(Exception):
            self.svc.unfollow(uuid4(), "ghost")

    def test_update_profile_bio(self):
        user = make_user()
        self.users.find_by_id.return_value = user
        self.users.save.return_value = user

        from src.application.dtos import UpdateProfileRequest
        result = self.svc.update_profile(user.id, UpdateProfileRequest(bio="New bio"))
        assert result.bio == "New bio"

    def test_update_profile_not_found_raises(self):
        self.users.find_by_id.return_value = None

        from src.application.dtos import UpdateProfileRequest
        with pytest.raises(Exception):
            self.svc.update_profile(uuid4(), UpdateProfileRequest(bio="x"))

    def test_follow_sends_notification(self):
        follower = make_user()
        target = make_user(username="target", email="t@t.com")
        self.users.find_by_username.return_value = target
        self.users.find_by_id.return_value = follower
        self.follows.is_following.return_value = False

        self.svc.follow(follower.id, "target")
        self.notify.send_new_follower.assert_called_once()

    def test_get_followers_not_found_raises(self):
        self.users.find_by_username.return_value = None

        with pytest.raises(Exception):
            self.svc.get_followers("ghost", 1, 20)

    def test_get_following_not_found_raises(self):
        self.users.find_by_username.return_value = None

        with pytest.raises(Exception):
            self.svc.get_following("ghost", 1, 20)