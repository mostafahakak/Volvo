from django.db import migrations, models


def copy_maintenance_type_fk_to_m2m(apps, schema_editor):
    MaintenanceSchedule = apps.get_model("app", "MaintenanceSchedule")
    for row in MaintenanceSchedule.objects.exclude(maintenance_type_id=None):
        row.maintenance_types.add(row.maintenance_type_id)


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0034_service_category_and_services_bilingual"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenanceschedule",
            name="maintenance_types",
            field=models.ManyToManyField(
                blank=True,
                related_name="maintenance_schedules",
                to="app.maintenancescheduletype",
            ),
        ),
        migrations.RunPython(copy_maintenance_type_fk_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="maintenanceschedule",
            name="maintenance_type",
        ),
    ]
