# Katameya rename, Arabic service menu, periodic maintenance range & line items.

from django.db import migrations


def forwards(apps, schema_editor):
    Branches = apps.get_model("user", "Branches")
    Services = apps.get_model("app", "Services")

    b = Branches.objects.filter(name="Qatamya").first()
    if b:
        b.name = "Katameya"
        if hasattr(b, "address") and b.address in ("Qatamya", None, ""):
            b.address = "القطامية"
        b.save()

    kat = Branches.objects.filter(name="Katameya").first()

    updates = [
        (
            "Seyana dawraya",
            {
                "name": "صيانة دورية",
                "min_price": 20000,
                "max_price": 30000,
                "line_items_ar": "زيت، فلتر زيت، فلتر بنزين",
                "price_note_ar": "بيتحدد السعر النهائي على حسب نوع الخامات المستخدمة",
                "only_at_branch": None,
            },
        ),
        (
            "Ta2rer ba3 we shara",
            {
                "name": "تقرير بيع و شراء",
                "min_price": 0,
                "max_price": 0,
                "line_items_ar": "",
                "price_note_ar": "",
                "only_at_branch": None,
            },
        ),
        (
            "Esla7at 3ama",
            {
                "name": "اصلاحات عامة",
                "min_price": 0,
                "max_price": 0,
                "line_items_ar": "",
                "price_note_ar": "",
                "only_at_branch": None,
            },
        ),
        (
            "Samkara we dehan",
            {
                "name": "سمكرة و دهان",
                "min_price": 0,
                "max_price": 0,
                "line_items_ar": "",
                "price_note_ar": "",
                "only_at_branch": kat,
            },
        ),
        (
            "Accessories",
            {
                "name": "اكسسوارات",
                "min_price": 0,
                "max_price": 0,
                "line_items_ar": "",
                "price_note_ar": "",
                "only_at_branch": None,
            },
        ),
    ]
    for old_name, fields in updates:
        s = Services.objects.filter(name=old_name).first()
        if not s:
            continue
        only_b = fields.pop("only_at_branch", None)
        for k, v in fields.items():
            setattr(s, k, v)
        s.only_at_branch = only_b
        s.save()

    extras = [
        ("كشف على العفشة", 0, 0),
        ("كشف على الفرامل", 0, 0),
    ]
    for name, mn, mx in extras:
        Services.objects.get_or_create(
            name=name,
            defaults={
                "price": 0,
                "min_price": mn,
                "max_price": mx,
                "points": 10,
            },
        )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0019_booking_workflow_service_branch_rules"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
