# Generated manually for catalog images on accessories / special offers

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0029_home_banner_and_carousel_heading"),
    ]

    operations = [
        migrations.AddField(
            model_name="accessories",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="accessories"),
        ),
        migrations.AddField(
            model_name="accessories",
            name="image_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
