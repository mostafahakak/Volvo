# Ensures default dashboard staff exists after migrate (Render / any fresh DB).

from django.contrib.auth.hashers import make_password
from django.db import migrations

DASHBOARD_EMAIL = "Admin@volvoegypt.com"
DASHBOARD_MOBILE = "+201000000001"
DASHBOARD_PASSWORD = "12345678"


def seed_dashboard_admin(apps, schema_editor):
    User = apps.get_model("user", "User")
    hashed = make_password(DASHBOARD_PASSWORD)

    u = User.objects.filter(email__iexact=DASHBOARD_EMAIL).first()
    if not u:
        u = User.objects.filter(mobile=DASHBOARD_MOBILE).first()

    if u:
        u.email = DASHBOARD_EMAIL
        u.is_staff = True
        u.is_superuser = True
        u.is_active = True
        u.password = hashed
        if not u.mobile:
            u.mobile = DASHBOARD_MOBILE
        u.save()
        return

    username_base = f"admin_{DASHBOARD_MOBILE.replace('+', '')}"
    username = username_base
    n = 0
    while User.objects.filter(username=username).exists():
        n += 1
        username = f"{username_base}_{n}"

    User.objects.create(
        username=username,
        mobile=DASHBOARD_MOBILE,
        email=DASHBOARD_EMAIL,
        password=hashed,
        is_staff=True,
        is_superuser=True,
        is_active=True,
        first_name="Admin",
        last_name="Volvo",
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0018_user_next_service_fields"),
    ]

    operations = [
        migrations.RunPython(seed_dashboard_admin, noop_reverse),
    ]
