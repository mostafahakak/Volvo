# Generated manually

from django.db import migrations, models


def rename_default_branches(apps, schema_editor):
    Branches = apps.get_model("user", "Branches")
    renames = (
        ("Qatamya", "Katameya"),
        ("October", "6 October"),
    )
    for old, new in renames:
        Branches.objects.filter(name=old).update(name=new)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0023_usercars_verify_existing"),
    ]

    operations = [
        migrations.AddField(
            model_name="branches",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="branches",
            name="maps_url",
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
        migrations.RunPython(rename_default_branches, noop_reverse),
    ]
