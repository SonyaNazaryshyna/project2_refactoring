"""Post domain entity — Rich Domain Model."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from src.domain.exceptions import DomainException


class PostStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DELETED = "DELETED"


@dataclass
class Post:
    """Rich domain entity for a microblog post."""

    id: UUID
    author_id: UUID
    content: str
    status: PostStatus
    like_count: int
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[UUID] = None  # for replies

    MAX_CONTENT_LENGTH = 280

    @classmethod
    def create(cls, author_id: UUID, content: str, parent_id: Optional[UUID] = None) -> "Post":
        """Factory method — validates and creates a new post."""
        cls._validate_content(content)
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            author_id=author_id,
            content=content,
            status=PostStatus.PUBLISHED,
            like_count=0,
            created_at=now,
            updated_at=now,
            parent_id=parent_id,
        )

    @staticmethod
    def _validate_content(content: str) -> None:
        if not content or not content.strip():
            raise DomainException("Post content cannot be empty.")
        if len(content) > Post.MAX_CONTENT_LENGTH:
            raise DomainException(f"Post content cannot exceed {Post.MAX_CONTENT_LENGTH} characters.")

    def edit(self, new_content: str) -> None:
        """Business rule: only PUBLISHED posts can be edited."""
        if self.status != PostStatus.PUBLISHED:
            raise DomainException("Only published posts can be edited.")
        self._validate_content(new_content)
        self.content = new_content
        self.updated_at = datetime.utcnow()

    def delete(self) -> None:
        """Soft delete — business logic lives here, not in the service."""
        if self.status == PostStatus.DELETED:
            raise DomainException("Post is already deleted.")
        self.status = PostStatus.DELETED
        self.updated_at = datetime.utcnow()

    def increment_likes(self) -> None:
        if self.status != PostStatus.PUBLISHED:
            raise DomainException("Cannot like a non-published post.")
        self.like_count += 1

    def decrement_likes(self) -> None:
        if self.like_count <= 0:
            raise DomainException("Like count cannot go below zero.")
        self.like_count -= 1

    @property
    def is_reply(self) -> bool:
        return self.parent_id is not None
