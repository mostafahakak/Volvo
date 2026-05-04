from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0027_serviceitem_price_booking_selections"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicecategory",
            name="icon_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name="services",
            name="icons_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name="maintenanceschedule",
            name="description_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
