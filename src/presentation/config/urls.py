from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from src.presentation.controllers import user_views
from src.presentation.controllers import frontend_views
from src.presentation.controllers import auth_views
from src.presentation.controllers import post_views

urlpatterns = [
    # Frontend
    path("", frontend_views.feed_view),
    path("login", frontend_views.login_view),
    path("register", frontend_views.register_view),
    path("logout", frontend_views.logout_view),
    path("explore", frontend_views.explore_view),
    path("search", frontend_views.search_view),
    path("profile", frontend_views.my_profile_view),
    path("user/<str:username>", frontend_views.user_profile_view),
    path("user/<str:username>/edit", frontend_views.update_profile_view),
    path("user/<str:username>/followers", frontend_views.followers_view),
    path("user/<str:username>/following", frontend_views.following_view),
    # Admin panel
    path("admin-panel", frontend_views.admin_panel_view),
    path("admin-panel/ban/<str:username>", frontend_views.admin_ban_view),
    path("admin-panel/unban/<str:username>", frontend_views.admin_unban_view),
    path("admin-panel/delete/<str:username>", frontend_views.admin_delete_view),
    # Django admin
    path("admin/", admin.site.urls),
    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Auth API
    path("api/v1/auth/register", auth_views.register),
    path("api/v1/auth/login", auth_views.login),
    path("api/v1/auth/refresh", auth_views.refresh_token),
    # Posts API
    # path("api/v1/posts", post_views.posts_list),
    # path("api/v1/posts/<str:post_id>", post_views.post_detail),
    # path("api/v1/posts/<str:post_id>/like", post_views.post_like),
    # path("api/v1/feed", post_views.feed),
    path("api/v1/posts/", post_views.posts_list_get),
    path("api/v1/posts/create/", post_views.posts_list_create),
    path("api/v1/posts/<str:post_id>/", post_views.post_detail_get),
    path("api/v1/posts/<str:post_id>/edit/", post_views.post_detail_edit),
    path("api/v1/posts/<str:post_id>/delete/", post_views.post_detail_delete),
    path("api/v1/posts/<str:post_id>/like/", post_views.post_like_add),     
    path("api/v1/posts/<str:post_id>/unlike/", post_views.post_like_remove),
    # Users API
    path("api/v1/users/me", user_views.me),
    path("api/v1/users/me/update", user_views.update_me),
    path("api/v1/users/<str:username>", user_views.user_profile),
    path("api/v1/users/<str:username>/follow", user_views.follow_user),
    path("api/v1/users/<str:username>/followers", user_views.user_followers),
    path("api/v1/users/<str:username>/following", user_views.user_following),
]
