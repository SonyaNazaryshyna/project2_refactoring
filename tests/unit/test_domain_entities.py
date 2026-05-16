"""Unit tests — Domain Entities."""
import pytest
from datetime import datetime
from uuid import uuid4

from src.domain.entities.post import Post, PostStatus
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from src.domain.exceptions import DomainException


# ══════════════════════════════════════════
# EMAIL VALUE OBJECT
# ══════════════════════════════════════════

class TestEmail:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert str(e) == "user@example.com"

    def test_valid_email_with_dots(self):
        e = Email("user.name+tag@sub.domain.com")
        assert e.value == "user.name+tag@sub.domain.com"

    def test_invalid_no_at(self):
        with pytest.raises(DomainException):
            Email("userexample.com")

    def test_invalid_no_domain(self):
        with pytest.raises(DomainException):
            Email("user@")

    def test_invalid_empty(self):
        with pytest.raises(DomainException):
            Email("")

    def test_invalid_spaces(self):
        with pytest.raises(DomainException):
            Email("user @example.com")

    def test_email_immutable(self):
        e = Email("user@example.com")
        with pytest.raises(Exception):
            e.value = "other@example.com"

    def test_email_equality(self):
        assert Email("a@b.com") == Email("a@b.com")

    def test_email_inequality(self):
        assert Email("a@b.com") != Email("c@b.com")


# ══════════════════════════════════════════
# USERNAME VALUE OBJECT
# ══════════════════════════════════════════

class TestUsername:
    def test_valid_username(self):
        u = Username("sofia_dev")
        assert str(u) == "sofia_dev"

    def test_valid_min_length(self):
        u = Username("abc")
        assert u.value == "abc"

    def test_valid_max_length(self):
        u = Username("a" * 30)
        assert len(u.value) == 30

    def test_invalid_too_short(self):
        with pytest.raises(DomainException):
            Username("ab")

    def test_invalid_too_long(self):
        with pytest.raises(DomainException):
            Username("a" * 31)

    def test_invalid_special_chars(self):
        with pytest.raises(DomainException):
            Username("user-name!")

    def test_invalid_spaces(self):
        with pytest.raises(DomainException):
            Username("user name")

    def test_invalid_empty(self):
        with pytest.raises(DomainException):
            Username("")

    def test_valid_numbers(self):
        u = Username("user123")
        assert u.value == "user123"

    def test_valid_underscore(self):
        u = Username("user_name_99")
        assert u.value == "user_name_99"

    def test_username_immutable(self):
        u = Username("sofia")
        with pytest.raises(Exception):
            u.value = "other"

    def test_username_equality(self):
        assert Username("sofia") == Username("sofia")


# ══════════════════════════════════════════
# USER ENTITY
# ══════════════════════════════════════════

class TestUserCreate:
    def test_create_valid_user(self):
        u = User.create("sofia", "sofia@test.com", "hash123")
        assert str(u.username) == "sofia"
        assert str(u.email) == "sofia@test.com"
        assert u.is_active is True
        assert u.bio == ""
        assert u.avatar_url is None
        assert u.id is not None

    def test_create_with_bio(self):
        u = User.create("sofia", "sofia@test.com", "hash", bio="Hello!")
        assert u.bio == "Hello!"

    def test_create_generates_unique_ids(self):
        u1 = User.create("user1", "u1@test.com", "h")
        u2 = User.create("user2", "u2@test.com", "h")
        assert u1.id != u2.id

    def test_create_sets_created_at(self):
        u = User.create("sofia", "sofia@test.com", "h")
        assert isinstance(u.created_at, datetime)

    def test_create_invalid_email_raises(self):
        with pytest.raises(DomainException):
            User.create("sofia", "not-an-email", "h")

    def test_create_invalid_username_raises(self):
        with pytest.raises(DomainException):
            User.create("ab", "sofia@test.com", "h")


class TestUserDeactivate:
    def test_deactivate_active_user(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.deactivate()
        assert u.is_active is False

    def test_deactivate_already_inactive_raises(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.deactivate()
        with pytest.raises(DomainException):
            u.deactivate()


class TestUserUpdateBio:
    def test_update_bio_valid(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.update_bio("New bio!")
        assert u.bio == "New bio!"

    def test_update_bio_empty(self):
        u = User.create("sofia", "sofia@test.com", "h", bio="Old")
        u.update_bio("")
        assert u.bio == ""

    def test_update_bio_max_length(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.update_bio("x" * 500)
        assert len(u.bio) == 500

    def test_update_bio_too_long_raises(self):
        u = User.create("sofia", "sofia@test.com", "h")
        with pytest.raises(DomainException):
            u.update_bio("x" * 501)


class TestUserAvatar:
    def test_update_avatar(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.update_avatar("https://example.com/pic.jpg")
        assert u.avatar_url == "https://example.com/pic.jpg"

    def test_update_avatar_replaces_old(self):
        u = User.create("sofia", "sofia@test.com", "h")
        u.update_avatar("https://old.com/pic.jpg")
        u.update_avatar("https://new.com/pic.jpg")
        assert u.avatar_url == "https://new.com/pic.jpg"


class TestUserCounters:
    def test_follower_count_default(self):
        u = User.create("sofia", "sofia@test.com", "h")
        assert u.follower_count == 0

    def test_following_count_default(self):
        u = User.create("sofia", "sofia@test.com", "h")
        assert u.following_count == 0


# ══════════════════════════════════════════
# POST ENTITY
# ══════════════════════════════════════════

class TestPostCreate:
    def test_create_valid_post(self):
        p = Post.create(author_id=uuid4(), content="Hello world!")
        assert p.content == "Hello world!"
        assert p.status == PostStatus.PUBLISHED
        assert p.like_count == 0
        assert p.id is not None
        assert p.is_reply is False

    def test_create_with_max_content(self):
        p = Post.create(author_id=uuid4(), content="x" * 280)
        assert len(p.content) == 280

    def test_create_exceeds_max_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="x" * 281)

    def test_create_empty_content_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="")

    def test_create_whitespace_only_raises(self):
        with pytest.raises(DomainException):
            Post.create(author_id=uuid4(), content="   ")

    def test_create_sets_timestamps(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        assert isinstance(p.created_at, datetime)
        assert isinstance(p.updated_at, datetime)

    def test_create_reply_post(self):
        parent_id = uuid4()
        p = Post.create(author_id=uuid4(), content="Reply!", parent_id=parent_id)
        assert p.is_reply is True
        assert p.parent_id == parent_id

    def test_create_unique_ids(self):
        a = uuid4()
        p1 = Post.create(author_id=a, content="One")
        p2 = Post.create(author_id=a, content="Two")
        assert p1.id != p2.id


class TestPostLikes:
    def test_increment_likes(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.increment_likes()
        assert p.like_count == 1

    def test_increment_likes_multiple(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.increment_likes()
        p.increment_likes()
        p.increment_likes()
        assert p.like_count == 3

    def test_decrement_likes(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.increment_likes()
        p.decrement_likes()
        assert p.like_count == 0

    def test_decrement_below_zero_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        with pytest.raises(DomainException):
            p.decrement_likes()

    def test_like_deleted_post_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.delete()
        with pytest.raises(DomainException):
            p.increment_likes()

    def test_like_count_not_negative(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.increment_likes()
        p.decrement_likes()
        assert p.like_count == 0


class TestPostEdit:
    def test_edit_content(self):
        p = Post.create(author_id=uuid4(), content="Original")
        p.edit("Updated content")
        assert p.content == "Updated content"

    def test_edit_updates_timestamp(self):
        p = Post.create(author_id=uuid4(), content="Original")
        old_ts = p.updated_at
        import time; time.sleep(0.01)
        p.edit("Updated")
        assert p.updated_at >= old_ts

    def test_edit_deleted_post_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.delete()
        with pytest.raises(DomainException):
            p.edit("New content")

    def test_edit_empty_content_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        with pytest.raises(DomainException):
            p.edit("")

    def test_edit_too_long_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        with pytest.raises(DomainException):
            p.edit("x" * 281)

    def test_edit_max_length_ok(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.edit("x" * 280)
        assert len(p.content) == 280


class TestPostDelete:
    def test_delete_published_post(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.delete()
        assert p.status == PostStatus.DELETED

    def test_delete_twice_raises(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.delete()
        with pytest.raises(DomainException):
            p.delete()

    def test_delete_updates_timestamp(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        old_ts = p.updated_at
        import time; time.sleep(0.01)
        p.delete()
        assert p.updated_at >= old_ts

    def test_deleted_post_status(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        p.delete()
        assert p.status == PostStatus.DELETED
        assert p.status != PostStatus.PUBLISHED


class TestPostIsReply:
    def test_not_reply_by_default(self):
        p = Post.create(author_id=uuid4(), content="Hi")
        assert p.is_reply is False

    def test_is_reply_with_parent(self):
        p = Post.create(author_id=uuid4(), content="Hi", parent_id=uuid4())
        assert p.is_reply is True

    def test_parent_id_stored(self):
        parent = uuid4()
        p = Post.create(author_id=uuid4(), content="Hi", parent_id=parent)
        assert p.parent_id == parent