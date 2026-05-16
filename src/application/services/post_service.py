"""PostService — orchestrates post use cases."""

from __future__ import annotations
from uuid import UUID

from src.application.dtos import (
    CreatePostRequest,
    EditPostRequest,
    PostResponse,
    PaginatedResponse,
)
from src.domain.entities.post import Post
from src.domain.exceptions import DomainException
from src.domain.ports import PostRepository, LikeRepository, UserRepository


class NotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class PostService:
    def __init__(
        self,
        post_repo: PostRepository,
        like_repo: LikeRepository,
        user_repo: UserRepository,
    ) -> None:
        self._posts = post_repo
        self._likes = like_repo
        self._users = user_repo

    def create_post(self, author_id: UUID, req: CreatePostRequest) -> PostResponse:
        post = Post.create(
            author_id=author_id,
            content=req.content,
            parent_id=req.parent_id,
        )
        saved = self._posts.save(post)
        author = self._users.find_by_id(author_id)
        return self._to_response(saved, str(author.username), False)

    def edit_post(self, user_id: UUID, post_id: UUID, req: EditPostRequest) -> PostResponse:
        post = self._get_or_raise(post_id)
        if post.author_id != user_id:
            raise ForbiddenError("You can only edit your own posts.")
        post.edit(req.content)
        saved = self._posts.save(post)
        author = self._users.find_by_id(user_id)
        liked = self._likes.has_liked(user_id, post_id)
        return self._to_response(saved, str(author.username), liked)

    def delete_post(self, user_id: UUID, post_id: UUID) -> None:
        post = self._get_or_raise(post_id)
        if post.author_id != user_id:
            raise ForbiddenError("You can only delete your own posts.")
        post.delete()
        self._posts.save(post)

    def like_post(self, user_id: UUID, post_id: UUID) -> None:
        post = self._get_or_raise(post_id)
        if self._likes.has_liked(user_id, post_id):
            raise DomainException("Post is already liked.")
        post.increment_likes()
        self._posts.save(post)
        self._likes.like(user_id, post_id)

    def unlike_post(self, user_id: UUID, post_id: UUID) -> None:
        post = self._get_or_raise(post_id)
        if not self._likes.has_liked(user_id, post_id):
            raise DomainException("Post is not liked yet.")
        post.decrement_likes()
        self._posts.save(post)
        self._likes.unlike(user_id, post_id)

    def get_feed(self, user_id: UUID, page: int, size: int) -> PaginatedResponse:
        posts = self._posts.find_feed(user_id, page, size)
        items = []
        for p in posts:
            author = self._users.find_by_id(p.author_id)
            liked = self._likes.has_liked(user_id, p.id)
            items.append(self._to_response(p, str(author.username) if author else "deleted", liked))
        return PaginatedResponse(items=items, total=len(items), page=page, size=size, pages=1)

    def get_user_posts(self, viewer_id: UUID, author_id: UUID, page: int, size: int) -> PaginatedResponse:
        posts = self._posts.find_by_author(author_id, page, size)
        author = self._users.find_by_id(author_id)
        author_name = str(author.username) if author else "deleted"
        items = []
        for p in posts:
            liked = self._likes.has_liked(viewer_id, p.id)
            items.append(self._to_response(p, author_name, liked))
        return PaginatedResponse(items=items, total=len(items), page=page, size=size, pages=1)

    def _get_or_raise(self, post_id: UUID) -> Post:
        post = self._posts.find_by_id(post_id)
        if post is None:
            raise NotFoundError(f"Post {post_id} not found.")
        return post

    @staticmethod
    def _to_response(post: Post, author_username: str, is_liked: bool) -> PostResponse:
        return PostResponse(
            id=post.id,
            author_id=post.author_id,
            author_username=author_username,
            content=post.content,
            status=post.status.value,
            like_count=post.like_count,
            is_liked_by_me=is_liked,
            is_reply=post.is_reply,
            parent_id=post.parent_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
