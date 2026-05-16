"""Django ORM models — infrastructure layer only."""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra):
        user = self.model(email=self.normalize_email(email), username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "ROLE_ADMIN")
        return self.create_user(email, username, password, **extra)


class UserORM(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [("ROLE_USER", "User"), ("ROLE_ADMIN", "Admin")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="ROLE_USER")
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username


class PostORM(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
        ("DELETED", "Deleted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(UserORM, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=280)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PUBLISHED")
    like_count = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"
        indexes = [models.Index(fields=["author", "-created_at"])]

    def __str__(self):
        return f"{self.author.username}: {self.content[:40]}"


class FollowORM(models.Model):
    follower = models.ForeignKey(UserORM, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(UserORM, on_delete=models.CASCADE, related_name="follower_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follows"
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]


class LikeORM(models.Model):
    user = models.ForeignKey(UserORM, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(PostORM, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "likes"
        unique_together = ("user", "post")
