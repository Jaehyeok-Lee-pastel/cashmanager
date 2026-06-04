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


def month_bounds(month: str) -> tuple[str, str]:
    """Return [start, end) ISO date strings for a "YYYY-MM" month.

    end is the first day of the next month (exclusive upper bound).
    """
    year, mon = (int(part) for part in month.split("-", 1))
    start = date(year, mon, 1)
    end = date(year + 1, 1, 1) if mon == 12 else date(year, mon + 1, 1)
    return start.isoformat(), end.isoformat()
