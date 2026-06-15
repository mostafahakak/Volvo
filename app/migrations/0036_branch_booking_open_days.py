from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0029_fix_egypt_mobile_e164"),
        ("app", "0035_maintenance_types_m2m"),
    ]

    operations = [
        migrations.CreateModel(
            name="BranchBookingOpenDay",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField(db_index=True)),
                (
                    "branch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="booking_open_days",
                        to="user.branches",
                    ),
                ),
            ],
            options={
                "ordering": ["date", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="branchbookingopenday",
            constraint=models.UniqueConstraint(
                fields=("branch", "date"),
                name="uniq_branch_booking_open_day",
            ),
        ),
    ]
