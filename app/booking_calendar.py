"""Helpers for branch booking calendars and hourly time slots."""

from datetime import date, time, timedelta

from app.models import BranchBookingOpenDay, Timing

# Hourly appointment slots: 9:00 through 18:00 (9 AM – 6 PM).
BOOKING_HOUR_START = 9
BOOKING_HOUR_END = 18


def booking_hours_range():
    return range(BOOKING_HOUR_START, BOOKING_HOUR_END + 1)


def parse_booking_date(date_str):
    if not date_str or not isinstance(date_str, str):
        raise ValueError("date must be YYYY-MM-DD")
    return date.fromisoformat(date_str.strip())


def is_friday(d):
    return d.weekday() == 4


def branch_has_open_day_calendar(branch_id):
    return BranchBookingOpenDay.objects.filter(branch_id=branch_id).exists()


def branch_date_is_open(branch, d):
    """If the branch has any open-day rows, only those dates are bookable."""
    if not branch_has_open_day_calendar(branch.id):
        return not is_friday(d)
    return BranchBookingOpenDay.objects.filter(branch=branch, date=d).exists()


def ensure_branch_timings(branch):
    """Ensure hourly Timing rows exist for 9:00–18:00 at this branch."""
    for hour in booking_hours_range():
        Timing.objects.get_or_create(branch=branch, time=time(hour, 0))


def normalize_booking_hours(hours):
    if hours is None:
        return list(booking_hours_range())
    out = []
    for h in hours:
        try:
            hi = int(h)
        except (TypeError, ValueError):
            continue
        if BOOKING_HOUR_START <= hi <= BOOKING_HOUR_END:
            out.append(hi)
    return sorted(set(out)) if out else list(booking_hours_range())


def timings_for_hours(branch, hours):
    ensure_branch_timings(branch)
    hour_set = set(normalize_booking_hours(hours))
    return Timing.objects.filter(branch=branch, time__hour__in=hour_set).order_by("time")


def get_open_day(branch, d):
    return (
        BranchBookingOpenDay.objects.filter(branch=branch, date=d)
        .prefetch_related("enabled_times")
        .first()
    )


def timings_for_open_date(branch, d):
    """Timings bookable on a specific date (open-day calendar)."""
    open_day = get_open_day(branch, d)
    if not open_day:
        return Timing.objects.none()
    if open_day.enabled_times.exists():
        return open_day.enabled_times.all().order_by("time")
    ensure_branch_timings(branch)
    return timings_for_hours(branch, list(booking_hours_range()))


def timings_for_branch_on_date(branch, d):
    """Resolve timings for the app list API (calendar vs legacy)."""
    if branch_has_open_day_calendar(branch.id):
        return timings_for_open_date(branch, d)
    ensure_branch_timings(branch)
    return Timing.objects.filter(branch=branch).order_by("time")


def open_day_row_dict(row):
    times = sorted(
        [t for t in row.enabled_times.all() if t.time],
        key=lambda t: t.time,
    )
    enabled_hours = [t.time.hour for t in times]
    return {
        "id": row.id,
        "branch_id": row.branch_id,
        "branch_name": row.branch.name if row.branch else "",
        "date": row.date.isoformat(),
        "enabled_hours": enabled_hours,
        "enabled_time_ids": [t.id for t in times],
        "slots_label": ", ".join(f"{h:02d}:00" for h in enabled_hours) if enabled_hours else "—",
    }


def iter_dates_inclusive(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
