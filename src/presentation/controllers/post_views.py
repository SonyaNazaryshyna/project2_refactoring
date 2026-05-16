"""Post REST controllers."""

from uuid import UUID
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from src.application.dtos import CreatePostRequest, EditPostRequest
from src.presentation.config.container import get_post_service
from src.infrastructure.database.models import PostORM
from src.infrastructure.database.repositories import DjangoLikeRepository


def _all_posts(viewer_id, page=1, size=40):
    """Return ALL published posts sorted by newest, with like info."""
    offset = (page - 1) * size
    qs = (
        PostORM.objects.filter(status="PUBLISHED")
        .select_related("author")
        .order_by("-created_at")[offset : offset + size]
    )
    like_repo = DjangoLikeRepository()
    items = []
    for p in qs:
        items.append(
            {
                "id": str(p.id),
                "author_id": str(p.author_id),
                "author_username": p.author.username,
                "content": p.content,
                "status": p.status,
                "like_count": p.like_count,
                "is_liked_by_me": like_repo.has_liked(viewer_id, p.id),
                "is_reply": p.parent_id is not None,
                "parent_id": str(p.parent_id) if p.parent_id else None,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
        )
    return {"items": items, "total": len(items), "page": page, "size": size, "pages": 1}


@api_view(["GET", "POST"])
def posts_list(request):
    """GET → all posts (explore). POST → create."""
    if request.method == "GET":
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 40))
        return Response(_all_posts(request.user.id, page, size))

    svc = get_post_service()
    req = CreatePostRequest(**request.data)
    post = svc.create_post(author_id=request.user.id, req=req)
    return Response(post.model_dump(), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def post_detail(request, post_id: str):
    svc = get_post_service()
    pid = UUID(post_id)
    if request.method == "GET":
        post = svc._get_or_raise(pid)
        from src.infrastructure.database.repositories import DjangoUserRepository

        author = DjangoUserRepository().find_by_id(post.author_id)
        liked = DjangoLikeRepository().has_liked(request.user.id, pid)
        return Response(svc._to_response(post, str(author.username), liked).model_dump())
    if request.method == "PATCH":
        req = EditPostRequest(**request.data)
        post = svc.edit_post(user_id=request.user.id, post_id=pid, req=req)
        return Response(post.model_dump())
    svc.delete_post(user_id=request.user.id, post_id=pid)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST", "DELETE"])
def post_like(request, post_id: str):
    svc = get_post_service()
    pid = UUID(post_id)
    if request.method == "POST":
        svc.like_post(user_id=request.user.id, post_id=pid)
        return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)
    svc.unlike_post(user_id=request.user.id, post_id=pid)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def feed(request):
    """Personal feed — posts from followed users."""
    svc = get_post_service()
    page = int(request.query_params.get("page", 1))
    size = int(request.query_params.get("size", 30))
    result = svc.get_feed(user_id=request.user.id, page=page, size=size)
    return Response(result.model_dump())
