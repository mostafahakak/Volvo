# Seed catalog car models (Volvo lineup, 2013–present era). Safe to re-run: skips existing names.

from django.db import migrations


VOLVO_MODEL_NAMES = [
    "Volvo XC90",
    "Volvo XC90 Recharge",
    "Volvo XC60",
    "Volvo XC60 Recharge",
    "Volvo XC40",
    "Volvo XC40 Recharge",
    "Volvo EX30",
    "Volvo EX90",
    "Volvo C40 Recharge",
    "Volvo S90",
    "Volvo S90 Recharge",
    "Volvo S60",
    "Volvo S60 Recharge",
    "Volvo V90 Cross Country",
    "Volvo V90",
    "Volvo V60 Cross Country",
    "Volvo V60",
    "Volvo V40",
    "Volvo V40 Cross Country",
    "Volvo S80",
    "Volvo V70",
    "Volvo XC70",
]


def seed_models(apps, schema_editor):
    CarModels = apps.get_model("user", "CarModels")
    for name in VOLVO_MODEL_NAMES:
        if not CarModels.objects.filter(car_model=name).exists():
            CarModels.objects.create(car_model=name)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0015_usercars_document_urls"),
    ]

    operations = [
        migrations.RunPython(seed_models, noop_reverse),
    ]
