from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0020_carmodels_year_type_details"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="next_service_date",
            field=models.DateField(
                blank=True,
                default=timezone.localdate,
                null=True,
            ),
        ),
    ]
