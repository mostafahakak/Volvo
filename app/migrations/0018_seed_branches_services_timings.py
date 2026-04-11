# Seed Qatamya / Abo Rawash / October branches, service menu, 12:00–18:00 hourly timings (7 slots), 3 branch slots.

from datetime import time

from django.db import migrations


def forwards(apps, schema_editor):
    Branches = apps.get_model("user", "Branches")
    Timing = apps.get_model("app", "Timing")
    BranchSlot = apps.get_model("app", "BranchSlot")
    Services = apps.get_model("app", "Services")

    branch_specs = [
        ("Qatamya", "30.0", "31.0", "Qatamya"),
        ("Abo Rawash", "30.1", "31.1", "Abo Rawash"),
        ("October", "30.2", "31.2", "6th October"),
    ]
    branches = []
    for name, lat, lng, addr in branch_specs:
        b, _ = Branches.objects.get_or_create(
            name=name,
            defaults={
                "latitude": lat,
                "langitude": lng,
                "address": addr,
                "mobile1": None,
                "mobile2": None,
            },
        )
        branches.append(b)

    service_names = [
        "Seyana dawraya",
        "Ta2rer ba3 we shara",
        "Esla7at 3ama",
        "Samkara we dehan",
        "Accessories",
    ]
    for sn in service_names:
        Services.objects.get_or_create(
            name=sn,
            defaults={"price": 0, "min_price": 0, "max_price": 0, "points": 10},
        )

    for b in branches:
        for h in range(12, 19):
            Timing.objects.get_or_create(
                branch=b,
                time=time(h, 0),
                defaults={},
            )
        for sn in (1, 2, 3):
            BranchSlot.objects.get_or_create(
                branch=b,
                slot_number=sn,
                defaults={},
            )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0017_booking_slot_index"),
        ("user", "0017_alter_user_email_optional"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
