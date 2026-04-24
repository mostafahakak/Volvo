from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0026_accessories_kind"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceitem",
            name="price",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="service_item_selections",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
