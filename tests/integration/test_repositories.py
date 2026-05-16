"""Integration tests — Django ORM Repositories."""
import pytest
from uuid import uuid4
from datetime import datetime, UTC

from src.domain.entities.user import User
from src.domain.entities.post import Post, PostStatus
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from src.infrastructure.database.repositories import (
    DjangoUserRepository,
    DjangoPostRepository,
    DjangoFollowRepository,
    DjangoLikeRepository,
)


def make_user_entity(username="testuser", email="test@example.com"):
    return User(
        id=uuid4(),
        username=Username(username),
        email=Email(email),
        password_hash="hashed_pw",
        bio="bio",
        avatar_url=None,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def make_post_entity(author_id):
    return Post.create(author_id=author_id, content="Test content")


# ══════════════════════════════════════════
# USER REPOSITORY
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestDjangoUserRepository:
    def setup_method(self):
        self.repo = DjangoUserRepository()

    def test_save_and_find_by_id(self):
        user = make_user_entity()
        saved = self.repo.save(user)
        found = self.repo.find_by_id(saved.id)
        assert found is not None
        assert str(found.username) == "testuser"

    def test_find_by_id_not_found(self):
        result = self.repo.find_by_id(uuid4())
        assert result is None

    def test_find_by_username(self):
        user = make_user_entity(username="uniqueuser", email="unique@example.com")
        self.repo.save(user)
        found = self.repo.find_by_username("uniqueuser")
        assert found is not None
        assert str(found.username) == "uniqueuser"

    def test_find_by_username_not_found(self):
        result = self.repo.find_by_username("ghost")
        assert result is None

    def test_find_by_email(self):
        user = make_user_entity(username="emailuser", email="emailuser@example.com")
        self.repo.save(user)
        found = self.repo.find_by_email("emailuser@example.com")
        assert found is not None

    def test_find_by_email_not_found(self):
        result = self.repo.find_by_email("ghost@ghost.com")
        assert result is None

    def test_exists_by_username_true(self):
        user = make_user_entity(username="existsuser", email="exists@example.com")
        self.repo.save(user)
        assert self.repo.exists_by_username("existsuser") is True

    def test_exists_by_username_false(self):
        assert self.repo.exists_by_username("nobody") is False

    def test_exists_by_email_true(self):
        user = make_user_entity(username="emailexists", email="emailexists@example.com")
        self.repo.save(user)
        assert self.repo.exists_by_email("emailexists@example.com") is True

    def test_exists_by_email_false(self):
        assert self.repo.exists_by_email("nobody@nobody.com") is False

    def test_save_updates_existing(self):
        user = make_user_entity(username="updateuser", email="update@example.com")
        saved = self.repo.save(user)
        saved.bio = "updated bio"
        updated = self.repo.save(saved)
        assert updated.bio == "updated bio"


# ══════════════════════════════════════════
# POST REPOSITORY
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestDjangoPostRepository:
    def setup_method(self):
        self.user_repo = DjangoUserRepository()
        self.post_repo = DjangoPostRepository()
        self.user = self.user_repo.save(
            make_user_entity(username="postauthor", email="postauthor@example.com")
        )

    def test_save_and_find_by_id(self):
        post = make_post_entity(self.user.id)
        saved = self.post_repo.save(post)
        found = self.post_repo.find_by_id(saved.id)
        assert found is not None
        assert found.content == "Test content"

    def test_find_by_id_not_found(self):
        result = self.post_repo.find_by_id(uuid4())
        assert result is None

    def test_find_by_author(self):
        post = make_post_entity(self.user.id)
        self.post_repo.save(post)
        posts = self.post_repo.find_by_author(self.user.id, page=1, size=10)
        assert len(posts) >= 1

    def test_find_by_author_empty(self):
        posts = self.post_repo.find_by_author(uuid4(), page=1, size=10)
        assert posts == []

    def test_find_feed(self):
        posts = self.post_repo.find_feed(self.user.id, page=1, size=10)
        assert isinstance(posts, list)

    def test_delete_post(self):
        post = make_post_entity(self.user.id)
        saved = self.post_repo.save(post)
        self.post_repo.delete(saved.id)
        found = self.post_repo.find_by_id(saved.id)
        assert found.status == PostStatus.DELETED

    def test_pagination(self):
        for i in range(5):
            p = Post.create(author_id=self.user.id, content=f"Post {i}")
            self.post_repo.save(p)
        page1 = self.post_repo.find_by_author(self.user.id, page=1, size=3)
        page2 = self.post_repo.find_by_author(self.user.id, page=2, size=3)
        assert len(page1) == 3
        assert len(page2) >= 2


# ══════════════════════════════════════════
# FOLLOW REPOSITORY
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestDjangoFollowRepository:
    def setup_method(self):
        self.user_repo = DjangoUserRepository()
        self.follow_repo = DjangoFollowRepository()
        self.user1 = self.user_repo.save(
            make_user_entity(username="follower", email="follower@example.com")
        )
        self.user2 = self.user_repo.save(
            make_user_entity(username="following", email="following@example.com")
        )

    def test_follow_and_is_following(self):
        self.follow_repo.follow(self.user1.id, self.user2.id)
        assert self.follow_repo.is_following(self.user1.id, self.user2.id) is True

    def test_not_following(self):
        assert self.follow_repo.is_following(self.user1.id, self.user2.id) is False

    def test_unfollow(self):
        self.follow_repo.follow(self.user1.id, self.user2.id)
        self.follow_repo.unfollow(self.user1.id, self.user2.id)
        assert self.follow_repo.is_following(self.user1.id, self.user2.id) is False

    def test_get_followers(self):
        self.follow_repo.follow(self.user1.id, self.user2.id)
        followers = self.follow_repo.get_followers(self.user2.id, page=1, size=10)
        assert any(str(u.username) == "follower" for u in followers)

    def test_get_following(self):
        self.follow_repo.follow(self.user1.id, self.user2.id)
        following = self.follow_repo.get_following(self.user1.id, page=1, size=10)
        assert any(str(u.username) == "following" for u in following)

    def test_follow_idempotent(self):
        self.follow_repo.follow(self.user1.id, self.user2.id)
        self.follow_repo.follow(self.user1.id, self.user2.id)
        assert self.follow_repo.is_following(self.user1.id, self.user2.id) is True


# ══════════════════════════════════════════
# LIKE REPOSITORY
# ══════════════════════════════════════════

@pytest.mark.django_db
class TestDjangoLikeRepository:
    def setup_method(self):
        self.user_repo = DjangoUserRepository()
        self.post_repo = DjangoPostRepository()
        self.like_repo = DjangoLikeRepository()
        self.user = self.user_repo.save(
            make_user_entity(username="likeuser", email="likeuser@example.com")
        )
        post = make_post_entity(self.user.id)
        self.post = self.post_repo.save(post)

    def test_like_and_has_liked(self):
        self.like_repo.like(self.user.id, self.post.id)
        assert self.like_repo.has_liked(self.user.id, self.post.id) is True

    def test_not_liked(self):
        assert self.like_repo.has_liked(self.user.id, self.post.id) is False

    def test_unlike(self):
        self.like_repo.like(self.user.id, self.post.id)
        self.like_repo.unlike(self.user.id, self.post.id)
        assert self.like_repo.has_liked(self.user.id, self.post.id) is False

    def test_like_idempotent(self):
        self.like_repo.like(self.user.id, self.post.id)
        self.like_repo.like(self.user.id, self.post.id)
        assert self.like_repo.has_liked(self.user.id, self.post.id) is True