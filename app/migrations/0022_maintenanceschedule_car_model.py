import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0020_carmodels_year_type_details"),
        ("app", "0021_site_contact_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenanceschedule",
            name="car_model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="maintenance_schedules",
                to="user.carmodels",
            ),
        ),
    ]
