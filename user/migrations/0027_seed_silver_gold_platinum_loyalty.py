# Ensures mobile app + dashboard share the same default tiers (thresholds match loyalty_tier_lookup).

from django.db import migrations


def seed_tiers(apps, schema_editor):
    LoyaltyPoints = apps.get_model("user", "LoyaltyPoints")
    tiers = (
        ("silver", 0, 10),
        ("gold", 2000, 15),
        ("platinum", 5000, 20),
    )
    for typ, point, ppp in tiers:
        LoyaltyPoints.objects.get_or_create(
            type=typ,
            defaults={"point": point, "point_per_pound": ppp},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0026_branches_lat_lng_optional"),
    ]

    operations = [
        migrations.RunPython(seed_tiers, noop_reverse),
    ]
