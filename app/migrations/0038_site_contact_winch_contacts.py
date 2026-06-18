from django.db import migrations, models


def seed_winch_contacts_from_legacy(apps, schema_editor):
    SiteContactSettings = apps.get_model("app", "SiteContactSettings")
    for row in SiteContactSettings.objects.all():
        if isinstance(row.winch_contacts, list) and row.winch_contacts:
            continue
        contacts = []
        p1 = (row.winch_primary or "").strip()
        p2 = (row.winch_secondary or "").strip()
        if p1:
            contacts.append({"name": "Line 1", "phone_e164": p1})
        if p2:
            contacts.append({"name": "Line 2", "phone_e164": p2})
        row.winch_contacts = contacts
        row.save(update_fields=["winch_contacts"])


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0037_open_day_enabled_times"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitecontactsettings",
            name="winch_contacts",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Roadside/winch phone list shown in the app.",
            ),
        ),
        migrations.RunPython(seed_winch_contacts_from_legacy, migrations.RunPython.noop),
    ]

