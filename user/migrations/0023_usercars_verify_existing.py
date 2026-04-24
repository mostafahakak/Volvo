# Existing vehicles were implicitly usable before the is_verified flag. Mark them verified;
# new rows keep default is_verified=False.

from django.db import migrations


def verify_existing(apps, schema_editor):
    UserCars = apps.get_model("user", "UserCars")
    UserCars.objects.filter(is_verified=False).update(is_verified=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0022_usercars_is_verified"),
    ]

    operations = [
        migrations.RunPython(verify_existing, noop_reverse),
    ]
