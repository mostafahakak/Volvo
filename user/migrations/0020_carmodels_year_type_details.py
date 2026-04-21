from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0019_seed_dashboard_admin"),
    ]

    operations = [
        migrations.AddField(
            model_name="carmodels",
            name="year_from",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="carmodels",
            name="year_to",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="carmodels",
            name="model_type",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="carmodels",
            name="details",
            field=models.TextField(blank=True, null=True),
        ),
    ]
