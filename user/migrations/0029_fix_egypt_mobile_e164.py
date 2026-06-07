# Repair Egypt mobiles corrupted by stripping the 0 in +2010... → +201...

from django.db import migrations

from user.phone_utils import repair_egypt_mobile_stripped_zero


def fix_corrupted_egypt_mobiles(apps, schema_editor):
    User = apps.get_model("user", "User")
    for user in User.objects.exclude(mobile__isnull=True).exclude(mobile="").iterator():
        fixed = repair_egypt_mobile_stripped_zero(user.mobile)
        if not fixed or fixed == user.mobile:
            continue
        if User.objects.filter(mobile=fixed).exclude(pk=user.pk).exists():
            continue
        user.mobile = fixed
        user.save(update_fields=["mobile"])


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0028_carmodels_image_url"),
    ]

    operations = [
        migrations.RunPython(fix_corrupted_egypt_mobiles, migrations.RunPython.noop),
    ]
