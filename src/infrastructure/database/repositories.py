"""Django ORM repository implementations."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.entities.user import User
from src.domain.entities.post import Post, PostStatus
from src.domain.ports import UserRepository, PostRepository, FollowRepository, LikeRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username
from src.infrastructure.database.models import UserORM, PostORM, FollowORM, LikeORM


def _orm_to_user(orm: UserORM) -> User:
    follower_count = orm.follower_set.count()
    following_count = orm.following_set.count()
    u = User(
        id=orm.id,
        username=Username(orm.username),
        email=Email(orm.email),
        password_hash=orm.password,
        bio=orm.bio,
        avatar_url=orm.avatar_url,
        is_active=orm.is_active,
        created_at=orm.created_at,
        _follower_count=follower_count,
        _following_count=following_count,
    )
    return u


def _orm_to_post(orm: PostORM) -> Post:
    return Post(
        id=orm.id,
        author_id=orm.author_id,
        content=orm.content,
        status=PostStatus(orm.status),
        like_count=orm.like_count,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        parent_id=orm.parent_id,
    )


class DjangoUserRepository(UserRepository):
    def save(self, user: User) -> User:
        orm, _ = UserORM.objects.update_or_create(
            id=user.id,
            defaults={
                "username": str(user.username),
                "email": str(user.email),
                "password": user.password_hash,
                "bio": user.bio,
                "avatar_url": user.avatar_url,
                "is_active": user.is_active,
            },
        )
        return _orm_to_user(orm)

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            return _orm_to_user(UserORM.objects.get(id=user_id))
        except UserORM.DoesNotExist:
            return None

    def find_by_username(self, username: str) -> Optional[User]:
        try:
            return _orm_to_user(UserORM.objects.get(username=username))
        except UserORM.DoesNotExist:
            return None

    def find_by_email(self, email: str) -> Optional[User]:
        try:
            return _orm_to_user(UserORM.objects.get(email=email))
        except UserORM.DoesNotExist:
            return None

    def exists_by_username(self, username: str) -> bool:
        return UserORM.objects.filter(username=username).exists()

    def exists_by_email(self, email: str) -> bool:
        return UserORM.objects.filter(email=email).exists()


class DjangoPostRepository(PostRepository):
    def save(self, post: Post) -> Post:
        orm, _ = PostORM.objects.update_or_create(
            id=post.id,
            defaults={
                "author_id": post.author_id,
                "content": post.content,
                "status": post.status.value,
                "like_count": post.like_count,
                "parent_id": post.parent_id,
            },
        )
        return _orm_to_post(orm)

    def find_by_id(self, post_id: UUID) -> Optional[Post]:
        try:
            return _orm_to_post(PostORM.objects.get(id=post_id))
        except PostORM.DoesNotExist:
            return None

    def find_by_author(self, author_id: UUID, page: int, size: int) -> list[Post]:
        offset = (page - 1) * size
        qs = PostORM.objects.filter(author_id=author_id, status="PUBLISHED").order_by("-created_at")[offset:offset + size]
        return [_orm_to_post(p) for p in qs]

    def find_feed(self, user_id: UUID, page: int, size: int) -> list[Post]:
        following_ids = FollowORM.objects.filter(follower_id=user_id).values_list("following_id", flat=True)
        offset = (page - 1) * size
        qs = PostORM.objects.filter(author_id__in=following_ids, status="PUBLISHED").order_by("-created_at")[offset:offset + size]
        return [_orm_to_post(p) for p in qs]

    def delete(self, post_id: UUID) -> None:
        PostORM.objects.filter(id=post_id).update(status="DELETED")


class DjangoFollowRepository(FollowRepository):
    def follow(self, follower_id: UUID, following_id: UUID) -> None:
        FollowORM.objects.get_or_create(follower_id=follower_id, following_id=following_id)

    def unfollow(self, follower_id: UUID, following_id: UUID) -> None:
        FollowORM.objects.filter(follower_id=follower_id, following_id=following_id).delete()

    def is_following(self, follower_id: UUID, following_id: UUID) -> bool:
        return FollowORM.objects.filter(follower_id=follower_id, following_id=following_id).exists()

    def get_followers(self, user_id: UUID, page: int, size: int) -> list[User]:
        offset = (page - 1) * size
        qs = UserORM.objects.filter(following_set__following_id=user_id)[offset:offset + size]
        return [_orm_to_user(u) for u in qs]

    def get_following(self, user_id: UUID, page: int, size: int) -> list[User]:
        offset = (page - 1) * size
        qs = UserORM.objects.filter(follower_set__follower_id=user_id)[offset:offset + size]
        return [_orm_to_user(u) for u in qs]


class DjangoLikeRepository(LikeRepository):
    def like(self, user_id: UUID, post_id: UUID) -> None:
        LikeORM.objects.get_or_create(user_id=user_id, post_id=post_id)

    def unlike(self, user_id: UUID, post_id: UUID) -> None:
        LikeORM.objects.filter(user_id=user_id, post_id=post_id).delete()

    def has_liked(self, user_id: UUID, post_id: UUID) -> bool:
        return LikeORM.objects.filter(user_id=user_id, post_id=post_id).exists()
