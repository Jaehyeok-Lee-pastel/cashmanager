from datetime import date

from app.core.timeutils import clamp_day, cycle_bounds, cycle_progress, month_progress


def test_month_progress_current_month():
    assert month_progress("2026-06", date(2026, 6, 10)) == (10, 30)


def test_month_progress_past_month_is_complete():
    assert month_progress("2026-05", date(2026, 6, 10)) == (31, 31)


def test_month_progress_future_month_is_zero():
    assert month_progress("2026-07", date(2026, 6, 10)) == (0, 31)


def test_month_progress_leap_february():
    assert month_progress("2024-02", date(2024, 2, 15)) == (15, 29)


def test_month_progress_non_leap_february():
    assert month_progress("2025-02", date(2025, 3, 1)) == (28, 28)


def test_month_progress_last_day_counts_as_complete():
    # elapsed == total -> the caller's `elapsed < total` guard skips projection.
    assert month_progress("2026-06", date(2026, 6, 30)) == (30, 30)


def test_month_progress_year_boundary():
    assert month_progress("2025-12", date(2026, 1, 5)) == (31, 31)


def test_month_progress_before_noise_window():
    # day 5 is < the 7-day projection window (gating happens in summary_service).
    assert month_progress("2026-06", date(2026, 6, 5)) == (5, 30)


def test_clamp_day_month_end():
    assert clamp_day(2026, 2, 31) == 28  # Feb non-leap
    assert clamp_day(2024, 2, 31) == 29  # leap
    assert clamp_day(2026, 4, 31) == 30  # 30-day month
    assert clamp_day(2026, 3, 31) == 31  # back to 31 (no permanent drift)
    assert clamp_day(2026, 6, 10) == 10


def test_cycle_bounds_payday_10():
    assert cycle_bounds(date(2026, 6, 15), 10) == ("2026-06-10", "2026-07-10")
    assert cycle_bounds(date(2026, 6, 10), 10) == ("2026-06-10", "2026-07-10")  # payday = new cycle
    assert cycle_bounds(date(2026, 6, 5), 10) == ("2026-05-10", "2026-06-10")  # before payday


def test_cycle_bounds_year_boundary():
    assert cycle_bounds(date(2026, 1, 5), 10) == ("2025-12-10", "2026-01-10")
    assert cycle_bounds(date(2026, 12, 20), 10) == ("2026-12-10", "2027-01-10")


def test_cycle_bounds_clamp_payday_31():
    assert cycle_bounds(date(2026, 3, 30), 31) == ("2026-02-28", "2026-03-31")
    assert cycle_bounds(date(2026, 3, 31), 31) == ("2026-03-31", "2026-04-30")


def test_cycle_progress_days_left_identity():
    e, t = cycle_progress(date(2026, 6, 10), 10)
    assert (e, t) == (1, 30)
    assert t - e + 1 == 30  # days until next payday
    e, t = cycle_progress(date(2026, 7, 9), 10)
    assert (e, t) == (30, 30)
    assert t - e + 1 == 1
