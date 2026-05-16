"""Frontend views — server-side rendered Django templates."""

from __future__ import annotations
import base64
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from src.infrastructure.database.models import UserORM, PostORM, LikeORM, FollowORM
from src.infrastructure.database.repositories import (
    DjangoUserRepository,
    DjangoLikeRepository,
)
from src.infrastructure.security.jwt_provider import JWTProvider, JWTConfig
from src.infrastructure.security.password import PasswordEncoder
from src.application.services.auth_service import (
    AuthService,
    ConflictError,
    AuthenticationError,
)
from src.application.dtos import RegisterRequest, LoginRequest
from src.infrastructure.external.notification import CeleryNotificationSender
from django.conf import settings

ADMIN_PANEL_URL = "/admin-panel"
AUTH_LOGIN_HTML = "auth/login.html"
AUTH_REGISTER_HTML = "auth/register.html"
LOGIN = "/login"

def _get_jwt():
    cfg = JWTConfig(
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_ttl_seconds=int(settings.JWT_ACCESS_TTL.total_seconds()),
        refresh_ttl_seconds=int(settings.JWT_REFRESH_TTL.total_seconds()),
    )
    return JWTProvider(cfg)


def _token(request):
    return request.COOKIES.get("access_token")


def _me(request):
    """Get current user from cookie token directly via DB."""
    token = _token(request)
    if not token:
        return None
    try:
        import importlib

        jwt = importlib.import_module("jwt")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user = UserORM.objects.get(id=payload["sub"], is_active=True)
        follower_count = FollowORM.objects.filter(following=user).count()
        following_count = FollowORM.objects.filter(follower=user).count()
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "follower_count": follower_count,
            "following_count": following_count,
            "is_admin": user.role == "ROLE_ADMIN",
        }
    except Exception:
        return None


def _posts_to_list(qs, viewer_id):
    """Convert PostORM queryset to list of dicts."""
    like_repo = DjangoLikeRepository()
    result = []
    for p in qs:
        result.append(
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
                "created_at": p.created_at.strftime("%d.%m.%Y %H:%M"),
                "updated_at": p.updated_at.isoformat(),
            }
        )
    return result


# ── Auth ───────────────────────────────────────────────────────────────────────


@csrf_protect
def login_view(request):
    if _token(request):
        return redirect("/")
    if request.method == "POST":
        try:
            svc = AuthService(
                user_repo=DjangoUserRepository(),
                password_encoder=PasswordEncoder(),
                jwt_provider=_get_jwt(),
                notification_sender=CeleryNotificationSender(),
            )
            tokens = svc.login(
                LoginRequest(
                    email=request.POST.get("email", ""),
                    password=request.POST.get("password", ""),
                )
            )
            resp = redirect("/")
            resp.set_cookie("access_token", tokens.access_token, httponly=False, samesite="Lax", max_age=3600)
            return resp
        except AuthenticationError as e:
            return render(request, AUTH_LOGIN_HTML, {"error": str(e)})
        except Exception:
            return render(request, AUTH_LOGIN_HTML, {"error": "Невірний email або пароль"})
    return render(request, AUTH_LOGIN_HTML)


@csrf_protect
def register_view(request):
    if _token(request):
        return redirect("/")
    if request.method == "POST":
        try:
            svc = AuthService(
                user_repo=DjangoUserRepository(),
                password_encoder=PasswordEncoder(),
                jwt_provider=_get_jwt(),
                notification_sender=CeleryNotificationSender(),
            )
            tokens = svc.register(
                RegisterRequest(
                    username=request.POST.get("username", ""),
                    email=request.POST.get("email", ""),
                    password=request.POST.get("password", ""),
                    bio=request.POST.get("bio", ""),
                )
            )
            resp = redirect("/")
            resp.set_cookie("access_token", tokens.access_token, httponly=False, samesite="Lax", max_age=3600)
            return resp
        except ConflictError as e:
            return render(request, AUTH_REGISTER_HTML, {"error": str(e)})
        except Exception as e:
            return render(request, AUTH_REGISTER_HTML, {"error": str(e)})
    return render(request, AUTH_REGISTER_HTML)

def logout_view(request):
    resp = redirect(LOGIN)
    resp.delete_cookie("access_token")
    return resp


# ── Feed ───────────────────────────────────────────────────────────────────────


def feed_view(request):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    # Personal feed: posts from followed users
    following_ids = FollowORM.objects.filter(follower_id=user["id"]).values_list("following_id", flat=True)
    qs = (
        PostORM.objects.filter(author_id__in=following_ids, status="PUBLISHED")
        .select_related("author")
        .order_by("-created_at")[:30]
    )
    posts = _posts_to_list(qs, user["id"])
    return render(
        request,
        "feed/feed.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "posts": posts,
        },
    )


def explore_view(request):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    # ALL posts from everyone
    qs = PostORM.objects.filter(status="PUBLISHED").select_related("author").order_by("-created_at")[:50]
    posts = _posts_to_list(qs, user["id"])
    return render(
        request,
        "feed/explore.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "posts": posts,
        },
    )


# ── Search ─────────────────────────────────────────────────────────────────────


def search_view(request):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    query = request.GET.get("q", "").strip()
    users = []
    if query:
        qs = UserORM.objects.filter(username__icontains=query, is_active=True).exclude(id=user["id"])[:20]
        for u in qs:
            users.append(
                {
                    "username": u.username,
                    "email": u.email,
                    "bio": u.bio,
                    "avatar_url": u.avatar_url,
                    "follower_count": FollowORM.objects.filter(following=u).count(),
                }
            )
    return render(
        request,
        "feed/search.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "query": query,
            "users": users,
        },
    )


# ── Profile ────────────────────────────────────────────────────────────────────


def my_profile_view(request):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    return redirect(f"/user/{user['username']}")


def user_profile_view(request, username):
    current_user = _me(request)
    if not current_user:
        return redirect(LOGIN)
    try:
        profile_orm = UserORM.objects.get(username=username)
    except UserORM.DoesNotExist:
        return redirect("/")

    profile = {
        "id": str(profile_orm.id),
        "username": profile_orm.username,
        "email": profile_orm.email,
        "bio": profile_orm.bio,
        "avatar_url": profile_orm.avatar_url,
        "follower_count": FollowORM.objects.filter(following=profile_orm).count(),
        "following_count": FollowORM.objects.filter(follower=profile_orm).count(),
    }
    qs = PostORM.objects.filter(author=profile_orm, status="PUBLISHED").select_related("author").order_by("-created_at")
    posts = _posts_to_list(qs, current_user["id"])
    is_own = current_user["username"] == username
    is_following = (
        FollowORM.objects.filter(follower_id=current_user["id"], following=profile_orm).exists()
        if not is_own
        else False
    )

    return render(
        request,
        "profile/profile.html",
        {
            "user_logged_in": True,
            "current_user": current_user,
            "profile_user": profile,
            "posts": posts,
            "is_own": is_own,
            "is_following": is_following,
        },
    )


def _apply_profile_updates(user_orm, request, username):
    """Apply profile field updates. Returns error redirect URL or None."""
    new_username = request.POST.get("username", "").strip()
    bio = request.POST.get("bio", "").strip()
    avatar_file = request.FILES.get("avatar")

    if new_username and new_username != user_orm.username:
        if UserORM.objects.filter(username=new_username).exists():
            return f"/user/{username}?error=username_taken"
        user_orm.username = new_username

    if bio is not None:
        user_orm.bio = bio

    if avatar_file:
        content = avatar_file.read()
        mime = avatar_file.content_type or "image/jpeg"
        b64 = base64.b64encode(content).decode()
        user_orm.avatar_url = f"data:{mime};base64,{b64}"

    return None


@csrf_protect
def update_profile_view(request, username):
    current_user = _me(request)
    if not current_user or current_user["username"] != username:
        return redirect(LOGIN)
    if request.method != "POST":
        return redirect(f"/user/{username}")
    try:
        user_orm = UserORM.objects.get(id=current_user["id"])
        error_url = _apply_profile_updates(user_orm, request, username)
        if error_url:
            return redirect(error_url)
        user_orm.save()
        return redirect(f"/user/{user_orm.username}")
    except Exception:
        return redirect(f"/user/{username}")

def followers_view(request, username):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    try:
        profile_orm = UserORM.objects.get(username=username)
    except UserORM.DoesNotExist:
        return redirect("/")
    followers_qs = UserORM.objects.filter(following_set__following=profile_orm)
    users = [
        {
            "username": u.username,
            "bio": u.bio,
            "avatar_url": u.avatar_url,
            "follower_count": FollowORM.objects.filter(following=u).count(),
        }
        for u in followers_qs
    ]
    return render(
        request,
        "profile/follow_list.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "username": username,
            "title": "Підписники",
            "users": users,
        },
    )


def following_view(request, username):
    user = _me(request)
    if not user:
        return redirect(LOGIN)
    try:
        profile_orm = UserORM.objects.get(username=username)
    except UserORM.DoesNotExist:
        return redirect("/")
    following_qs = UserORM.objects.filter(follower_set__follower=profile_orm)
    users = [
        {
            "username": u.username,
            "bio": u.bio,
            "avatar_url": u.avatar_url,
            "follower_count": FollowORM.objects.filter(following=u).count(),
        }
        for u in following_qs
    ]
    return render(
        request,
        "profile/follow_list.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "username": username,
            "title": "Підписки",
            "users": users,
        },
    )


# ── Admin panel ────────────────────────────────────────────────────────────────


def admin_panel_view(request):
    user = _me(request)
    if not user or not user.get("is_admin"):
        return redirect("/")
    query = request.GET.get("q", "").strip()
    users_qs = UserORM.objects.all().order_by("-id")
    if query:
        users_qs = users_qs.filter(username__icontains=query)
    users = []
    for u in users_qs:
        users.append(
            {
                "username": u.username,
                "email": u.email,
                "is_active": u.is_active,
                "created_at": u.created_at.strftime("%d.%m.%Y"),
                "post_count": PostORM.objects.filter(author=u).count(),
            }
        )
    recent_posts_qs = PostORM.objects.filter(status="PUBLISHED").select_related("author").order_by("-created_at")[:10]
    stats = {
        "total_users": UserORM.objects.count(),
        "total_posts": PostORM.objects.filter(status="PUBLISHED").count(),
        "total_likes": LikeORM.objects.count(),
        "total_follows": FollowORM.objects.count(),
    }
    return render(
        request,
        "admin_panel/dashboard.html",
        {
            "user_logged_in": True,
            "current_user": user,
            "users": users,
            "query": query,
            "stats": stats,
            "recent_posts": _posts_to_list(recent_posts_qs, user["id"]),
        },
    )


@require_http_methods(["POST"])
@csrf_protect
def admin_ban_view(request, username):
    user = _me(request)
    if not user or not user.get("is_admin"):
        return redirect("/")
    UserORM.objects.filter(username=username).update(is_active=False)
    return redirect(ADMIN_PANEL_URL)


@require_http_methods(["POST"])
@csrf_protect
def admin_unban_view(request, username):
    user = _me(request)
    if not user or not user.get("is_admin"):
        return redirect("/")
    UserORM.objects.filter(username=username).update(is_active=True)
    return redirect(ADMIN_PANEL_URL)


@require_http_methods(["POST"])
@csrf_protect
def admin_delete_view(request, username):
    user = _me(request)
    if not user or not user.get("is_admin"):
        return redirect("/")
    if username != user["username"]:
        UserORM.objects.filter(username=username).delete()
    return redirect(ADMIN_PANEL_URL)
