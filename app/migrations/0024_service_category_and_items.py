from django.db import migrations, models
import django.db.models.deletion


def seed_categories_from_existing_services(apps, schema_editor):
    Services = apps.get_model("app", "Services")
    ServiceCategory = apps.get_model("app", "ServiceCategory")

    # For each existing "service" row (conceptually a category today),
    # create a ServiceCategory with the same name and link the row back to it.
    # Admins can later delete / rename / replace these as they build the real catalogue.
    order = 0
    for svc in Services.objects.all().order_by("id"):
        label = (svc.name or "").strip()
        if not label:
            continue
        cat, _ = ServiceCategory.objects.get_or_create(
            name=label,
            defaults={"sort_order": order},
        )
        if svc.category_id is None:
            svc.category_id = cat.id
            svc.save(update_fields=["category"])
        order += 1


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0020_carmodels_year_type_details"),
        ("app", "0023_sitecontactsettings_theme_and_points"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="وقت الانشاء")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Update Date/Time")),
                ("name", models.CharField(max_length=255)),
                ("icon", models.ImageField(blank=True, null=True, upload_to="service_categories")),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={
                "verbose_name_plural": "Service categories",
                "ordering": ("sort_order", "id"),
            },
        ),
        migrations.CreateModel(
            name="ServiceItem",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="وقت الانشاء")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Update Date/Time")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="services",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="app.servicecategory",
            ),
        ),
        migrations.AddField(
            model_name="services",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="services",
            name="compatible_with",
            field=models.ManyToManyField(blank=True, related_name="services", to="user.carmodels"),
        ),
        migrations.AddField(
            model_name="services",
            name="items",
            field=models.ManyToManyField(blank=True, related_name="services", to="app.serviceitem"),
        ),
        migrations.RunPython(seed_categories_from_existing_services, noop),
    ]
