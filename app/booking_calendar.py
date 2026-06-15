"""Helpers for branch booking calendars and hourly time slots."""

from datetime import date, time, timedelta

from app.models import BranchBookingOpenDay, Timing


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
    """Default appointment hours: 12:00–18:00 hourly (matches seed data)."""
    for hour in range(12, 19):
        Timing.objects.get_or_create(branch=branch, time=time(hour, 0))


def iter_dates_inclusive(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)
