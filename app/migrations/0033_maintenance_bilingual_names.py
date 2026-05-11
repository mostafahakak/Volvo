# Arabic display names for maintenance types & service items (EN fallback in app when empty)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0032_maintenance_types_and_schedule_extras"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenancescheduletype",
            name="name_ar",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="serviceitem",
            name="name_ar",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
