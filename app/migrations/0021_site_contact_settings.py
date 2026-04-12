# Site contact settings for dashboard / public API.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0020_seed_booking_services_ar"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteContactSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="وقت الانشاء",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Update Date/Time",
                    ),
                ),
                (
                    "whatsapp_e164",
                    models.CharField(blank=True, default="", max_length=32),
                ),
                (
                    "tech_hotline_e164",
                    models.CharField(blank=True, default="", max_length=32),
                ),
                (
                    "winch_primary",
                    models.CharField(blank=True, default="", max_length=64),
                ),
                (
                    "winch_secondary",
                    models.CharField(blank=True, default="", max_length=64),
                ),
            ],
            options={
                "verbose_name": "Site contact settings",
                "verbose_name_plural": "Site contact settings",
            },
        ),
    ]
