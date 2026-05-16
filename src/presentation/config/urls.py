"""URL configuration."""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from src.presentation.controllers import auth_views, post_views, user_views
from src.presentation.controllers import frontend_views

urlpatterns = [
    # ── Frontend ──────────────────────────────────────────────────────────────
    path("", frontend_views.feed_view),
    path("login", frontend_views.login_view),
    path("register", frontend_views.register_view),
    path("logout", frontend_views.logout_view),
    path("explore", frontend_views.explore_view),
    path("profile", frontend_views.my_profile_view),
    path("user/<str:username>", frontend_views.user_profile_view),
    path("user/<str:username>/followers", frontend_views.followers_view),
    path("user/<str:username>/following", frontend_views.following_view),
    # ── Admin ─────────────────────────────────────────────────────────────────
    path("admin/", admin.site.urls),
    # ── API docs ──────────────────────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # ── Auth API ──────────────────────────────────────────────────────────────
    path("api/v1/auth/register", auth_views.register),
    path("api/v1/auth/login", auth_views.login),
    path("api/v1/auth/refresh", auth_views.refresh_token),
    # ── Posts API ─────────────────────────────────────────────────────────────
    path("api/v1/posts", post_views.posts_list),
    path("api/v1/posts/<str:post_id>", post_views.post_detail),
    path("api/v1/posts/<str:post_id>/like", post_views.post_like),
    path("api/v1/feed", post_views.feed),
    # ── Users API ─────────────────────────────────────────────────────────────
    path("api/v1/users/me", user_views.me),
    path("api/v1/users/me/update", user_views.update_me),
    path("api/v1/users/<str:username>", user_views.user_profile),
    path("api/v1/users/<str:username>/follow", user_views.follow_user),
    path("api/v1/users/<str:username>/followers", user_views.user_followers),
    path("api/v1/users/<str:username>/following", user_views.user_following),
]
