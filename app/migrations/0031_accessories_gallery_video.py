from django.db import migrations, models


def copy_image_url_to_gallery(apps, schema_editor):
    Accessories = apps.get_model("app", "Accessories")
    for row in Accessories.objects.all().only("id", "image_url", "gallery_urls"):
        urls = row.gallery_urls or []
        if urls:
            continue
        u = (row.image_url or "").strip()
        if u:
            row.gallery_urls = [u]
            row.save(update_fields=["gallery_urls"])


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0030_accessories_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="accessories",
            name="gallery_urls",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="accessories",
            name="video_url",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.RunPython(copy_image_url_to_gallery, migrations.RunPython.noop),
    ]
