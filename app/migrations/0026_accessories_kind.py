# Generated manually

from django.db import migrations, models


def set_kind_from_discount(apps, schema_editor):
    Accessories = apps.get_model("app", "Accessories")
    for row in Accessories.objects.all():
        d = row.discount or 0
        row.kind = "special_offer" if d > 0 else "accessory"
        row.save(update_fields=["kind"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0025_booking_customer_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="accessories",
            name="kind",
            field=models.CharField(
                choices=[("accessory", "Accessory"), ("special_offer", "Special offer")],
                db_index=True,
                default="accessory",
                max_length=20,
            ),
        ),
        migrations.RunPython(set_kind_from_discount, noop_reverse),
    ]
