import pytest
from io import StringIO
from django.core.management import call_command
from src.infrastructure.database.models import UserORM

@pytest.mark.django_db
class TestPromoteAdminCommand:
    
    def test_promote_user_to_admin_success(self):
        """Перевірка успішного підвищення ролі існуючого користувача"""
        username = "test_user"
        UserORM.objects.create(username=username, role="ROLE_USER")
        
        out = StringIO()
        call_command("promote_admin", username, stdout=out)
        
        assert f"@{username} is now ROLE_ADMIN" in out.getvalue()
        
        user = UserORM.objects.get(username=username)
        assert user.role == "ROLE_ADMIN"

    def test_promote_user_not_found(self):
        """Перевірка поведінки, коли користувача не існує"""
        out = StringIO()
        username = "non_existent_user"
        
        call_command("promote_admin", username, stdout=out)
        
        assert f"User '{username}' not found" in out.getvalue()

    def test_promote_already_admin(self):
        """Перевірка, що команда працює коректно, якщо юзер вже адмін"""
        username = "already_admin"
        UserORM.objects.create(username=username, role="ROLE_ADMIN")
        
        out = StringIO()
        call_command("promote_admin", username, stdout=out)
        
        assert f"@{username} is now ROLE_ADMIN" in out.getvalue()
        user = UserORM.objects.get(username=username)
        assert user.role == "ROLE_ADMIN"