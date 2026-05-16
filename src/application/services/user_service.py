"""UserService — orchestrates profile and follow use cases."""
from __future__ import annotations
from uuid import UUID

from src.application.dtos import UserResponse, UpdateProfileRequest, PaginatedResponse
from src.application.services.post_service import NotFoundError
from src.domain.exceptions import DomainException
from src.domain.ports import UserRepository, FollowRepository, NotificationSender


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        follow_repo: FollowRepository,
        notification_sender: NotificationSender,
    ) -> None:
        self._users = user_repo
        self._follows = follow_repo
        self._notify = notification_sender

    def get_profile(self, username: str) -> UserResponse:
        user = self._users.find_by_username(username)
        if user is None:
            raise NotFoundError(f"User '{username}' not found.")
        return self._to_response(user)

    def update_profile(self, user_id: UUID, req: UpdateProfileRequest) -> UserResponse:
        user = self._users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if req.bio is not None:
            user.update_bio(req.bio)
        if req.avatar_url is not None:
            user.update_avatar(req.avatar_url)
        saved = self._users.save(user)
        return self._to_response(saved)

    def follow(self, follower_id: UUID, username: str) -> None:
        target = self._users.find_by_username(username)
        if target is None:
            raise NotFoundError(f"User '{username}' not found.")
        if target.id == follower_id:
            raise DomainException("You cannot follow yourself.")
        if self._follows.is_following(follower_id, target.id):
            raise DomainException("Already following this user.")
        self._follows.follow(follower_id, target.id)
        follower = self._users.find_by_id(follower_id)
        self._notify.send_new_follower(target, follower)

    def unfollow(self, follower_id: UUID, username: str) -> None:
        target = self._users.find_by_username(username)
        if target is None:
            raise NotFoundError(f"User '{username}' not found.")
        if not self._follows.is_following(follower_id, target.id):
            raise DomainException("Not following this user.")
        self._follows.unfollow(follower_id, target.id)

    def get_followers(self, username: str, page: int, size: int) -> PaginatedResponse:
        user = self._users.find_by_username(username)
        if user is None:
            raise NotFoundError(f"User '{username}' not found.")
        followers = self._follows.get_followers(user.id, page, size)
        return PaginatedResponse(
            items=[self._to_response(u) for u in followers],
            total=len(followers),
            page=page,
            size=size,
            pages=1,
        )

    def get_following(self, username: str, page: int, size: int) -> PaginatedResponse:
        user = self._users.find_by_username(username)
        if user is None:
            raise NotFoundError(f"User '{username}' not found.")
        following = self._follows.get_following(user.id, page, size)
        return PaginatedResponse(
            items=[self._to_response(u) for u in following],
            total=len(following),
            page=page,
            size=size,
            pages=1,
        )

    @staticmethod
    def _to_response(user) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=str(user.username),
            email=str(user.email),
            bio=user.bio,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            follower_count=user.follower_count,
            following_count=user.following_count,
            created_at=user.created_at,
        )
