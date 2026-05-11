# Arabic names/descriptions for service categories & bookable services (EN fallback in app when empty)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0033_maintenance_bilingual_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicecategory",
            name="name_ar",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="services",
            name="name_ar",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="services",
            name="description_ar",
            field=models.TextField(blank=True, null=True),
        ),
    ]
