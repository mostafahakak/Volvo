from django.db import migrations


def backfill_maintenance_services(apps, schema_editor):
    from app.maintenance_service_sync import sync_all_maintenance_schedules_to_services

    sync_all_maintenance_schedules_to_services()


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0039_service_source_maintenance"),
    ]

    operations = [
        migrations.RunPython(backfill_maintenance_services, migrations.RunPython.noop),
    ]
