import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates a superuser from environment variables if none exists"

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists; skipping."))
            return

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or "admin"
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or "admin@example.com"
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(self.style.ERROR("DJANGO_SUPERUSER_PASSWORD not set; cannot create superuser."))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
