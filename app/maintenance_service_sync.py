"""Keep bookable services in sync with maintenance schedules for Regular Maintenance."""

from __future__ import annotations

from app.models import MaintenanceSchedule, ServiceCategory, Services


def find_regular_maintenance_category():
    """Category used for auto-created bookable maintenance services."""
    for cat in ServiceCategory.objects.all().order_by("sort_order", "id"):
        name = (cat.name or "").strip().lower()
        name_ar = (cat.name_ar or "").strip()
        if name == "regular maintenance" or "regular maintenance" in name:
            return cat
        if name_ar == "صيانة دورية" or "صيانة دورية" in name_ar:
            return cat
        if "صيانة دورية" in (cat.name or ""):
            return cat
    return None


def _service_names_for_schedule(schedule: MaintenanceSchedule):
    types = list(schedule.maintenance_types.all().order_by("sort_order", "id"))
    if not types:
        return f"Maintenance schedule #{schedule.pk}", None
    en = ", ".join(t.name for t in types if (t.name or "").strip())
    ar_parts = [(t.name_ar or "").strip() for t in types if (t.name_ar or "").strip()]
    ar = ", ".join(ar_parts) if ar_parts else None
    return en or f"Maintenance schedule #{schedule.pk}", ar


def ensure_service_for_schedule(schedule: MaintenanceSchedule):
    """
    Create or update a bookable service under Regular Maintenance that mirrors
    this maintenance schedule (items, models, price).
    """
    category = find_regular_maintenance_category()
    if not category:
        return None

    name_en, name_ar = _service_names_for_schedule(schedule)
    svc = schedule.linked_services.order_by("id").first()
    if svc is None:
        svc = Services.objects.create(
            name=name_en,
            name_ar=name_ar,
            category=category,
            source_maintenance=schedule,
            price=schedule.approximate_price,
            points=10,
        )
    else:
        svc.name = name_en
        if name_ar:
            svc.name_ar = name_ar
        svc.category = category
        svc.source_maintenance = schedule
        if svc.price != schedule.approximate_price:
            svc.price = schedule.approximate_price
        svc.save(
            update_fields=["name", "name_ar", "category", "source_maintenance", "price"]
        )

    svc.items.set(schedule.service_items.all())
    svc.compatible_with.set(schedule.compatible_car_models.all())
    return svc


def remove_services_for_schedule(schedule: MaintenanceSchedule):
    """Remove auto-linked bookable services when a schedule is deleted."""
    schedule.linked_services.all().delete()


def sync_all_maintenance_schedules_to_services():
    qs = (
        MaintenanceSchedule.objects.all()
        .prefetch_related(
            "maintenance_types",
            "compatible_car_models",
            "service_items",
        )
        .order_by("id")
    )
    for row in qs:
        ensure_service_for_schedule(row)
