import pytest
from io import StringIO
from django.core.management import call_command
from src.infrastructure.database.models import UserORM


@pytest.mark.django_db
class TestPromoteAdminCommand:

    def test_promote_user_to_admin_success(self):
        username = "test_user"
        UserORM.objects.create(username=username, email="test@test.com", role="ROLE_USER", is_active=True)

        out = StringIO()
        call_command("make_admin", username, stdout=out)

        assert "ROLE_ADMIN" in out.getvalue()
        user = UserORM.objects.get(username=username)
        assert user.role == "ROLE_ADMIN"

    def test_promote_user_not_found(self):
        out = StringIO()
        username = "non_existent_user"

        call_command("make_admin", username, stdout=out)

        assert "not found" in out.getvalue()

    def test_promote_already_admin(self):
        username = "already_admin"
        UserORM.objects.create(username=username, email="admin@test.com", role="ROLE_ADMIN", is_active=True)

        out = StringIO()
        call_command("make_admin", username, stdout=out)

        assert "ROLE_ADMIN" in out.getvalue()
        user = UserORM.objects.get(username=username)
        assert user.role == "ROLE_ADMIN"