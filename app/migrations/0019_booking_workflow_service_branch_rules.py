# Booking workflow status + service branch exclusivity and Arabic price details.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_seed_branches_services_timings"),
    ]

    operations = [
        migrations.AddField(
            model_name="services",
            name="line_items_ar",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="services",
            name="price_note_ar",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="services",
            name="only_at_branch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exclusive_services",
                to="user.branches",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="workflow_status",
            field=models.CharField(
                choices=[
                    ("pending_confirmation", "Pending confirmation"),
                    ("confirmed", "Confirmed"),
                    ("in_progress", "In progress"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                db_index=True,
                default="pending_confirmation",
                max_length=32,
            ),
        ),
    ]
