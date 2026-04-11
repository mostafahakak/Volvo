# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0016_myhistory_using_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="slot_index",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
