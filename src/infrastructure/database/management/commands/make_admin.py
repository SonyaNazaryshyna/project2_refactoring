"""Integration tests — make_admin management command."""
import pytest
from io import StringIO
from django.core.management import call_command
from src.infrastructure.database.models import UserORM


def create_user(username, email, role="ROLE_USER"):
    return UserORM.objects.create(
        username=username,
        email=email,
        password="hashed",
        is_active=True,
        role=role,
    )


@pytest.mark.django_db
class TestMakeAdminCommand:
    def test_promote_existing_user(self):
        create_user("testuser", "test@test.com")
        out = StringIO()
        call_command("make_admin", "testuser", stdout=out)
        user = UserORM.objects.get(username="testuser")
        assert user.role == "ROLE_ADMIN"
        assert "ROLE_ADMIN" in out.getvalue()

    def test_promote_nonexistent_user(self):
        out = StringIO()
        call_command("make_admin", "ghost", stdout=out)
        assert "not found" in out.getvalue()

    def test_promote_already_admin(self):
        create_user("adminuser", "admin@test.com", role="ROLE_ADMIN")
        out = StringIO()
        call_command("make_admin", "adminuser", stdout=out)
        user = UserORM.objects.get(username="adminuser")
        assert user.role == "ROLE_ADMIN"