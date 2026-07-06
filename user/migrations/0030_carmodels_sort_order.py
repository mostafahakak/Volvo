from django.db import migrations, models


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


def backfill_sort_order(apps, schema_editor):
    CarModels = apps.get_model("user", "CarModels")
    order = 0
    seen_ids = set()
    for name in VOLVO_MODEL_NAMES:
        for model in CarModels.objects.filter(car_model=name).order_by("id"):
            if model.id in seen_ids:
                continue
            model.sort_order = order
            model.save(update_fields=["sort_order"])
            seen_ids.add(model.id)
            order += 1
    for model in CarModels.objects.exclude(id__in=seen_ids).order_by("car_model", "id"):
        model.sort_order = order
        model.save(update_fields=["sort_order"])
        order += 1


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0029_fix_egypt_mobile_e164"),
    ]

    operations = [
        migrations.AddField(
            model_name="carmodels",
            name="sort_order",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name="carmodels",
            options={"ordering": ("sort_order", "id")},
        ),
        migrations.RunPython(backfill_sort_order, noop_reverse),
    ]
