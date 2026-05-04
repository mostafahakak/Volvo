from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0028_catalog_media_firebase_urls"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeBanner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=255)),
                ("text", models.TextField(blank=True, default="")),
                ("image", models.ImageField(blank=True, null=True, upload_to="home_banners")),
                ("image_url", models.URLField(blank=True, max_length=2048, null=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={
                "ordering": ("sort_order", "id"),
            },
        ),
        migrations.AddField(
            model_name="sitecontactsettings",
            name="home_carousel_heading",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Title shown above the home promo carousel (dashboard Home banners tab).",
                max_length=255,
            ),
        ),
    ]
