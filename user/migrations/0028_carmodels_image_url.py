from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0027_seed_silver_gold_platinum_loyalty"),
    ]

    operations = [
        migrations.AddField(
            model_name="carmodels",
            name="image_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
