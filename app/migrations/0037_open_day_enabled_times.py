from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0036_branch_booking_open_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="branchbookingopenday",
            name="enabled_times",
            field=models.ManyToManyField(
                blank=True,
                related_name="booking_open_days",
                to="app.timing",
            ),
        ),
    ]
