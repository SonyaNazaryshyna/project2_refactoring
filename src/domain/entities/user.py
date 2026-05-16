"""User domain entity — Rich Domain Model (not anemic)."""
from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.domain.exceptions import DomainException
from src.domain.value_objects.email import Email
from src.domain.value_objects.username import Username

if TYPE_CHECKING:
    pass


@dataclass
class User:
    """Rich domain entity for a microblog user."""

    id: UUID
    username: Username
    email: Email
    password_hash: str
    bio: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime.datetime
    _follower_count: int = field(default=0, repr=False)
    _following_count: int = field(default=0, repr=False)

    @classmethod
    def create(cls, username: str, email: str, password_hash: str, bio: str = "") -> "User":
        """Factory method — validates and creates a new user."""
        return cls(
            id=uuid4(),
            username=Username(username),
            email=Email(email),
            password_hash=password_hash,
            bio=bio,
            avatar_url=None,
            is_active=True,
            created_at=datetime.datetime.now(datetime.UTC),
        )

    def deactivate(self) -> None:
        """Business logic: deactivate account."""
        if not self.is_active:
            raise DomainException("User is already inactive.")
        self.is_active = False

    def update_bio(self, bio: str) -> None:
        if len(bio) > 500:
            raise DomainException("Bio cannot exceed 500 characters.")
        self.bio = bio

    def update_avatar(self, url: str) -> None:
        if not url.startswith(("http://", "https://")):
            raise DomainException("Avatar URL must be a valid HTTP URL.")
        self.avatar_url = url

    @property
    def follower_count(self) -> int:
        return self._follower_count

    @property
    def following_count(self) -> int:
        return self._following_count
