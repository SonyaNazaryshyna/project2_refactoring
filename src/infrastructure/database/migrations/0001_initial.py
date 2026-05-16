"""Initial migration — creates all microblog tables."""
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserORM",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("username", models.CharField(max_length=30, unique=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("bio", models.TextField(blank=True, default="")),
                ("avatar_url", models.URLField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "role",
                    models.CharField(
                        choices=[("ROLE_USER", "User"), ("ROLE_ADMIN", "Admin")],
                        default="ROLE_USER",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "users"},
        ),
        migrations.CreateModel(
            name="PostORM",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("content", models.CharField(max_length=280)),
                (
                    "status",
                    models.CharField(
                        choices=[("DRAFT", "Draft"), ("PUBLISHED", "Published"), ("DELETED", "Deleted")],
                        default="PUBLISHED",
                        max_length=20,
                    ),
                ),
                ("like_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to="database.userorm",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to="database.postorm",
                    ),
                ),
            ],
            options={"db_table": "posts"},
        ),
        migrations.CreateModel(
            name="FollowORM",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "follower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following_set",
                        to="database.userorm",
                    ),
                ),
                (
                    "following",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="follower_set",
                        to="database.userorm",
                    ),
                ),
            ],
            options={"db_table": "follows"},
        ),
        migrations.CreateModel(
            name="LikeORM",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="database.postorm",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="database.userorm",
                    ),
                ),
            ],
            options={"db_table": "likes"},
        ),
        # Unique constraints
        migrations.AlterUniqueTogether(
            name="followorm",
            unique_together={("follower", "following")},
        ),
        migrations.AlterUniqueTogether(
            name="likeorm",
            unique_together={("user", "post")},
        ),
        # Indexes
        migrations.AddIndex(
            model_name="postorm",
            index=models.Index(fields=["author", "-created_at"], name="posts_author_created_idx"),
        ),
        migrations.AddIndex(
            model_name="followorm",
            index=models.Index(fields=["follower"], name="follows_follower_idx"),
        ),
        migrations.AddIndex(
            model_name="followorm",
            index=models.Index(fields=["following"], name="follows_following_idx"),
        ),
    ]
