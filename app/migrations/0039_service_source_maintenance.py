from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0038_site_contact_winch_contacts"),
    ]

    operations = [
        migrations.AddField(
            model_name="services",
            name="source_maintenance",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="linked_services",
                to="app.maintenanceschedule",
            ),
        ),
    ]
