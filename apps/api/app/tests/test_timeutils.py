from datetime import date

from app.core.timeutils import month_progress


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
