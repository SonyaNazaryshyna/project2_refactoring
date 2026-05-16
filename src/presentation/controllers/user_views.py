"""User/profile REST controllers."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from src.application.dtos import UpdateProfileRequest
from src.presentation.config.container import get_user_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    svc = get_user_service()
    profile = svc.get_profile(request.user.username)
    return Response(profile.model_dump())


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_me(request):
    svc = get_user_service()
    req = UpdateProfileRequest(**request.data)
    profile = svc.update_profile(user_id=request.user.id, req=req)
    return Response(profile.model_dump())


@api_view(["GET"])
@permission_classes([AllowAny])
def user_profile(request, username: str):
    svc = get_user_service()
    profile = svc.get_profile(username)
    return Response(profile.model_dump())


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def follow_user(request, username: str):
    svc = get_user_service()
    if request.method == "POST":
        svc.follow(follower_id=request.user.id, username=username)
        return Response({"message": f"Now following @{username}"}, status=status.HTTP_201_CREATED)
    svc.unfollow(follower_id=request.user.id, username=username)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_followers(request, username: str):
    svc = get_user_service()
    page = int(request.query_params.get("page", 1))
    size = int(request.query_params.get("size", 20))
    result = svc.get_followers(username=username, page=page, size=size)
    return Response(result.model_dump())


@api_view(["GET"])
@permission_classes([AllowAny])
def user_following(request, username: str):
    svc = get_user_service()
    page = int(request.query_params.get("page", 1))
    size = int(request.query_params.get("size", 20))
    result = svc.get_following(username=username, page=page, size=size)
    return Response(result.model_dump())
