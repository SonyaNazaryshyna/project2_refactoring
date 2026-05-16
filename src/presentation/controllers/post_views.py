"""Post REST controllers."""
from uuid import UUID
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from src.application.dtos import CreatePostRequest, EditPostRequest
from src.presentation.config.container import get_post_service


@api_view(["GET", "POST"])
def posts_list(request):
    svc = get_post_service()
    if request.method == "GET":
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 20))
        result = svc.get_user_posts(
            viewer_id=request.user.id,
            author_id=request.user.id,
            page=page,
            size=size,
        )
        return Response(result.model_dump())

    req = CreatePostRequest(**request.data)
    post = svc.create_post(author_id=request.user.id, req=req)
    return Response(post.model_dump(), status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def post_detail(request, post_id: str):
    svc = get_post_service()
    pid = UUID(post_id)

    if request.method == "GET":
        post = svc._get_or_raise(pid)
        from src.infrastructure.database.repositories import DjangoUserRepository, DjangoLikeRepository

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
    svc = get_post_service()
    page = int(request.query_params.get("page", 1))
    size = int(request.query_params.get("size", 20))
    result = svc.get_feed(user_id=request.user.id, page=page, size=size)
    return Response(result.model_dump())
