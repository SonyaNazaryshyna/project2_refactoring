"""Abstract repository interfaces (Ports) — no framework dependencies."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.user import User
from src.domain.entities.post import Post


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]: ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def exists_by_username(self, username: str) -> bool: ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool: ...


class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> Post: ...

    @abstractmethod
    def find_by_id(self, post_id: UUID) -> Optional[Post]: ...

    @abstractmethod
    def find_by_author(self, author_id: UUID, page: int, size: int) -> list[Post]: ...

    @abstractmethod
    def find_feed(self, user_id: UUID, page: int, size: int) -> list[Post]: ...

    @abstractmethod
    def delete(self, post_id: UUID) -> None: ...


class FollowRepository(ABC):
    @abstractmethod
    def follow(self, follower_id: UUID, following_id: UUID) -> None: ...

    @abstractmethod
    def unfollow(self, follower_id: UUID, following_id: UUID) -> None: ...

    @abstractmethod
    def is_following(self, follower_id: UUID, following_id: UUID) -> bool: ...

    @abstractmethod
    def get_followers(self, user_id: UUID, page: int, size: int) -> list[User]: ...

    @abstractmethod
    def get_following(self, user_id: UUID, page: int, size: int) -> list[User]: ...


class LikeRepository(ABC):
    @abstractmethod
    def like(self, user_id: UUID, post_id: UUID) -> None: ...

    @abstractmethod
    def unlike(self, user_id: UUID, post_id: UUID) -> None: ...

    @abstractmethod
    def has_liked(self, user_id: UUID, post_id: UUID) -> bool: ...


class NotificationSender(ABC):
    @abstractmethod
    def send_welcome(self, user: User) -> None: ...

    @abstractmethod
    def send_new_follower(self, user: User, follower: User) -> None: ...
