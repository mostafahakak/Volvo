# Generated manually for optional email (phone-first auth).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0016_seed_volvo_car_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                max_length=125,
                null=True,
                verbose_name="email address",
            ),
        ),
    ]
