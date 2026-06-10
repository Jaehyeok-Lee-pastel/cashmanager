import calendar
from datetime import date, datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def today_kst() -> date:
    """Current date in Korea Standard Time (the user's wall-clock day)."""
    return datetime.now(KST).date()


def datetime_now_iso() -> str:
    """Current UTC timestamp as an ISO string (for soft-delete markers)."""
    return datetime.now(timezone.utc).isoformat()


def prev_month(month: str, back: int = 1) -> str:
    """Shift a "YYYY-MM" month backward by `back` months."""
    year, mon = (int(p) for p in month.split("-", 1))
    idx = (year * 12 + (mon - 1)) - back
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def month_progress(month: str, today: date | None = None) -> tuple[int, int]:
    """(elapsed_days, total_days) for a "YYYY-MM" month relative to today (KST).

    Past month  -> (total, total) (complete).
    Future month -> (0, total).
    Current month -> (today's day-of-month, total).
    Month is parsed (not string-compared) so the calendar comparison is exact.
    """
    today = today or today_kst()
    year, mon = (int(part) for part in month.split("-", 1))
    total_days = calendar.monthrange(year, mon)[1]
    target = (year, mon)
    current = (today.year, today.month)
    if target < current:
        return total_days, total_days
    if target > current:
        return 0, total_days
    return today.day, total_days


def month_bounds(month: str) -> tuple[str, str]:
    """Return [start, end) ISO date strings for a "YYYY-MM" month.

    end is the first day of the next month (exclusive upper bound).
    """
    year, mon = (int(part) for part in month.split("-", 1))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start.isoformat(), end.isoformat()


# --- Pay-cycle helpers (anchor = payday 1~31; clamps to month-end like 윤달) ---

def clamp_day(year: int, mon: int, anchor: int) -> int:
    """Payday clamped to the month's last day (anchor=31 -> 28/29/30 in short
    months, back to 31 in long ones — no permanent drift). Same pattern as
    recurring_service's day-of-month clamp."""
    return min(anchor, calendar.monthrange(year, mon)[1])


def _shift_month(year: int, mon: int, delta: int) -> tuple[int, int]:
    idx = year * 12 + (mon - 1) + delta
    return idx // 12, idx % 12 + 1


def cycle_bounds(today: date, anchor: int) -> tuple[str, str]:
    """[start, end) ISO dates for the pay cycle containing `today`.

    start = most recent payday on/before today; end = next payday (exclusive).
    Mirrors month_bounds' [start, end) contract so the same range query works.
    """
    this_payday = clamp_day(today.year, today.month, anchor)
    if today.day >= this_payday:
        start = date(today.year, today.month, this_payday)
    else:
        py, pm = _shift_month(today.year, today.month, -1)
        start = date(py, pm, clamp_day(py, pm, anchor))
    ny, nm = _shift_month(start.year, start.month, 1)
    end = date(ny, nm, clamp_day(ny, nm, anchor))
    return start.isoformat(), end.isoformat()


def cycle_progress(today: date, anchor: int) -> tuple[int, int]:
    """(elapsed_days incl. today, total_days) for the cycle containing today.

    With these, `total - elapsed + 1` equals the days left until the next payday,
    so _safe_to_spend's existing denominator formula stays correct."""
    start_iso, end_iso = cycle_bounds(today, anchor)
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    return (today - start).days + 1, (end - start).days
