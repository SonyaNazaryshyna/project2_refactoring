from django.core.management.base import BaseCommand
from src.infrastructure.database.models import UserORM


class Command(BaseCommand):
    help = "Promote a user to ROLE_ADMIN"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        updated = UserORM.objects.filter(username=username).update(role="ROLE_ADMIN")
        if updated:
            self.stdout.write(self.style.SUCCESS(f"✅ @{username} is now ROLE_ADMIN"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ User '{username}' not found"))
