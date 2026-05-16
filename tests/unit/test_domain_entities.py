"""Unit tests for domain entities."""
import pytest
from uuid import uuid4
from src.domain.entities.post import Post, PostStatus
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from src.domain.exceptions import DomainException


# ── Post entity tests ──────────────────────────────────────────────────────────


class TestPostCreation:
    def test_create_valid_post(self):
        post = Post.create(author_id=uuid4(), content="Hello world!")
        assert post.content == "Hello world!"
        assert post.status == PostStatus.PUBLISHED
        assert post.like_count == 0
        assert post.id is not None

    def test_empty_content_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="")

    def test_whitespace_only_content_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="   ")

    def test_content_exceeds_280_chars_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="x" * 281)

    def test_exactly_280_chars_is_valid(self):
        post = Post.create(author_id=uuid4(), content="x" * 280)
        assert len(post.content) == 280

    def test_reply_post_has_parent_id(self):
        parent_id = uuid4()
        post = Post.create(author_id=uuid4(), content="Reply!", parent_id=parent_id)
        assert post.is_reply is True
        assert post.parent_id == parent_id


class TestPostLikes:
    def test_increment_likes(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.increment_likes()
        assert post.like_count == 1

    def test_decrement_likes(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.increment_likes()
        post.decrement_likes()
        assert post.like_count == 0

    def test_decrement_below_zero_raises(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        with pytest.raises(DomainException):
            post.decrement_likes()

    def test_cannot_like_deleted_post(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.delete()
        with pytest.raises(DomainException):
            post.increment_likes()


class TestPostLifecycle:
    def test_delete_post(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.delete()
        assert post.status == PostStatus.DELETED

    def test_double_delete_raises(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.delete()
        with pytest.raises(DomainException):
            post.delete()

    def test_edit_post(self):
        post = Post.create(author_id=uuid4(), content="Original")
        post.edit("Updated")
        assert post.content == "Updated"

    def test_cannot_edit_deleted_post(self):
        post = Post.create(author_id=uuid4(), content="Hi")
        post.delete()
        with pytest.raises(DomainException):
            post.edit("New content")


# ── Value Object tests ─────────────────────────────────────────────────────────


class TestEmailVO:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert str(e) == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(DomainException):
            Email("not-an-email")

    def test_email_is_immutable(self):
        e = Email("user@example.com")
        with pytest.raises(Exception):
            e.value = "other@example.com"


class TestUsernameVO:
    def test_valid_username(self):
        u = Username("john_doe")
        assert str(u) == "john_doe"

    def test_too_short_raises(self):
        with pytest.raises(DomainException):
            Username("ab")

    def test_too_long_raises(self):
        with pytest.raises(DomainException):
            Username("a" * 31)

    def test_special_chars_raises(self):
        with pytest.raises(DomainException):
            Username("john-doe!")
