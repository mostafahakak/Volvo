# Maintenance schedule types, M2M cars/items, approximate price

from django.db import migrations, models
import django.db.models.deletion


def copy_car_model_to_m2m(apps, schema_editor):
    MaintenanceSchedule = apps.get_model("app", "MaintenanceSchedule")
    for row in MaintenanceSchedule.objects.exclude(car_model_id__isnull=True).iterator():
        row.compatible_car_models.add(row.car_model_id)


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0028_carmodels_image_url"),
        ("app", "0031_accessories_gallery_video"),
    ]

    operations = [
        migrations.CreateModel(
            name="MaintenanceScheduleType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddField(
            model_name="maintenanceschedule",
            name="approximate_price",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="maintenanceschedule",
            name="maintenance_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="schedules",
                to="app.maintenancescheduletype",
            ),
        ),
        migrations.AddField(
            model_name="maintenanceschedule",
            name="compatible_car_models",
            field=models.ManyToManyField(
                blank=True,
                related_name="maintenance_schedule_entries",
                to="user.CarModels",
            ),
        ),
        migrations.AddField(
            model_name="maintenanceschedule",
            name="service_items",
            field=models.ManyToManyField(
                blank=True,
                related_name="maintenance_schedules_linked",
                to="app.ServiceItem",
            ),
        ),
        migrations.RunPython(copy_car_model_to_m2m, migrations.RunPython.noop),
    ]
