"""Temporary management command to create initial superuser.

This command creates a superuser if it doesn't exist.
It reads credentials from environment variables:
- DJANGO_SUPERUSER_EMAIL (required)
- DJANGO_SUPERUSER_PASSWORD (required)

Usage:
    python manage.py create_initial_superuser
"""

import os

from django.core.management.base import BaseCommand
from django.core.management import call_command

from saleor.account.utils import create_superuser


class Command(BaseCommand):
    help = "Create initial superuser from environment variables"

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_EMAIL environment variable is required"
                )
            )
            return

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_PASSWORD environment variable is required"
                )
            )
            return

        credentials = {"email": email, "password": password}
        msg = create_superuser(credentials)
        self.stdout.write(self.style.SUCCESS(msg))

