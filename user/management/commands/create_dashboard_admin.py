from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_EMAIL = "Admin@volvoegypt.com"
DEFAULT_PASSWORD = "12345678"
DEFAULT_MOBILE = "+201000000001"


class Command(BaseCommand):
    help = "Create or update the Volvo Egypt dashboard staff user (email + password login)."

    def handle(self, *args, **options):
        user = User.objects.filter(email__iexact=DEFAULT_EMAIL).first()
        if not user:
            user = User.objects.filter(mobile=DEFAULT_MOBILE).first()

        if user:
            user.email = DEFAULT_EMAIL
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if not user.mobile:
                user.mobile = DEFAULT_MOBILE
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated admin user id={user.pk} ({DEFAULT_EMAIL})."))
            return

        User.objects.create_superuser(
            mobile=DEFAULT_MOBILE,
            email=DEFAULT_EMAIL,
            password=DEFAULT_PASSWORD,
            first_name="Admin",
            last_name="Volvo",
        )
        self.stdout.write(self.style.SUCCESS(f"Created admin user {DEFAULT_EMAIL} / mobile {DEFAULT_MOBILE}."))
