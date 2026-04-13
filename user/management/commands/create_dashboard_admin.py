from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

DEFAULT_EMAIL = "Admin@volvoegypt.com"
DEFAULT_PASSWORD = "12345678"
DEFAULT_MOBILE = "+201000000001"


class Command(BaseCommand):
    help = (
        "Create or update a staff user for the Next.js admin dashboard (email + password). "
        "The email does not need to exist beforehand — this command inserts or updates the row."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=DEFAULT_EMAIL,
            help=f"Staff login email (default: {DEFAULT_EMAIL})",
        )
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help="Password to set",
        )
        parser.add_argument(
            "--mobile",
            default=DEFAULT_MOBILE,
            help=f"Unique mobile if creating a new user (default: {DEFAULT_MOBILE})",
        )

    def handle(self, *args, **options):
        email = (options["email"] or "").strip()
        password = options["password"] or ""
        mobile = (options["mobile"] or "").strip()

        if not email or not password or not mobile:
            self.stderr.write(self.style.ERROR("email, password, and mobile are required."))
            return

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(mobile=mobile).first()

        if user:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if not user.mobile:
                user.mobile = mobile
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated staff user id={user.pk} — login with {email} (mobile: {user.mobile})",
                )
            )
            return

        User.objects.create_superuser(
            mobile=mobile,
            email=email,
            password=password,
            first_name="Admin",
            last_name="Volvo",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created staff user — email: {email}, mobile: {mobile}. Use this email on /api/admin/login/."
            )
        )
