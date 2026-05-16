"""Frontend views — server-side rendered with Django templates."""
from __future__ import annotations
import requests
from django.shortcuts import render, redirect

API = "http://127.0.0.1:8000/api/v1"


def _api(path, token=None, method="GET", json=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.request(method, f"{API}{path}", headers=headers, json=json, timeout=5)
        return r.json() if r.content else {}, r.status_code
    except Exception:
        return {}, 500


def _token(request):
    return request.COOKIES.get("access_token")


def _me(request):
    token = _token(request)
    if not token:
        return None
    data, status = _api("/users/me", token=token)
    return data if status == 200 else None


# ── Auth ───────────────────────────────────────────────────────────────────────

def login_view(request):
    if _token(request):
        return redirect("/")
    if request.method == "POST":
        data, status = _api("/auth/login", method="POST", json={
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
        })
        if status == 200:
            resp = redirect("/")
            resp.set_cookie("access_token", data["access_token"],
                            httponly=False, samesite="Lax", max_age=3600)
            return resp
        return render(request, "auth/login.html",
                      {"error": data.get("message", "Невірний email або пароль")})
    return render(request, "auth/login.html")


def register_view(request):
    if _token(request):
        return redirect("/")
    if request.method == "POST":
        data, status = _api("/auth/register", method="POST", json={
            "username": request.POST.get("username"),
            "email":    request.POST.get("email"),
            "password": request.POST.get("password"),
            "bio":      request.POST.get("bio", ""),
        })
        if status == 201:
            resp = redirect("/")
            resp.set_cookie("access_token", data["access_token"],
                            httponly=False, samesite="Lax", max_age=3600)
            return resp
        return render(request, "auth/register.html",
                      {"error": data.get("message", "Помилка реєстрації")})
    return render(request, "auth/register.html")


def logout_view(request):
    resp = redirect("/login")
    resp.delete_cookie("access_token")
    return resp


# ── Feed ───────────────────────────────────────────────────────────────────────

def feed_view(request):
    user = _me(request)
    if not user:
        return redirect("/login")
    data, _ = _api("/feed?page=1&size=30", token=_token(request))
    return render(request, "feed/feed.html", {
        "user_logged_in": True,
        "current_user": user,
        "posts": data.get("items", []),
    })


def explore_view(request):
    user = _me(request)
    if not user:
        return redirect("/login")
    data, _ = _api("/posts?page=1&size=40", token=_token(request))
    return render(request, "feed/explore.html", {
        "user_logged_in": True,
        "current_user": user,
        "posts": data.get("items", []),
    })


# ── Profile ────────────────────────────────────────────────────────────────────

def my_profile_view(request):
    user = _me(request)
    if not user:
        return redirect("/login")
    return redirect(f"/user/{user['username']}")


def user_profile_view(request, username):
    current_user = _me(request)
    if not current_user:
        return redirect("/login")
    token = _token(request)

    profile, status = _api(f"/users/{username}", token=token)
    if status != 200:
        return redirect("/")

    # Get posts for this user
    all_data, _ = _api("/posts?page=1&size=100", token=token)
    posts = [p for p in all_data.get("items", [])
             if p.get("author_username") == username]

    is_own = current_user["username"] == username
    is_following = False
    if not is_own:
        flw, _ = _api(f"/users/{current_user['username']}/following?page=1&size=200", token=token)
        is_following = any(u.get("username") == username for u in flw.get("items", []))

    return render(request, "profile/profile.html", {
        "user_logged_in": True,
        "current_user": current_user,
        "profile_user": profile,
        "posts": posts,
        "is_own": is_own,
        "is_following": is_following,
    })


def followers_view(request, username):
    user = _me(request)
    if not user:
        return redirect("/login")
    data, _ = _api(f"/users/{username}/followers?page=1&size=100", token=_token(request))
    return render(request, "profile/follow_list.html", {
        "user_logged_in": True,
        "current_user": user,
        "username": username,
        "title": "Підписники",
        "users": data.get("items", []),
    })


def following_view(request, username):
    user = _me(request)
    if not user:
        return redirect("/login")
    data, _ = _api(f"/users/{username}/following?page=1&size=100", token=_token(request))
    return render(request, "profile/follow_list.html", {
        "user_logged_in": True,
        "current_user": user,
        "username": username,
        "title": "Підписки",
        "users": data.get("items", []),
    })
