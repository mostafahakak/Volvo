from django.db import migrations, models
from django.utils import timezone


def backfill_next_service_date(apps, schema_editor):
    User = apps.get_model("user", "User")
    for row in User.objects.filter(next_service_date__isnull=True).iterator():
        if row.date_joined:
            row.next_service_date = row.date_joined.date()
            row.save(update_fields=["next_service_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0017_alter_user_email_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="next_service_km",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="next_service_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_next_service_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="next_service_date",
            field=models.DateField(default=timezone.localdate),
        ),
    ]
