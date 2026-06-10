from datetime import date

import app.services.recurring_service as rs


def _rules(monkeypatch, rules):
    monkeypatch.setattr("app.repositories.recurring_repo.list_rules", lambda uid: rules)


def test_materialize_creates_only_due_and_unrecorded(monkeypatch):
    monkeypatch.setattr(rs, "today_kst", lambda: date(2026, 6, 15))
    _rules(monkeypatch, [
        {"id": "r1", "active": True, "direction": "expense", "category_id": None, "memo": "월세", "amount_minor": 500000, "day_of_month": 1},
        {"id": "r2", "active": True, "direction": "expense", "category_id": None, "memo": "넷플", "amount_minor": 13500, "day_of_month": 20},  # not due
        {"id": "r3", "active": True, "direction": "expense", "category_id": None, "memo": "보험", "amount_minor": 30000, "day_of_month": 10},  # recorded
        {"id": "r4", "active": False, "direction": "expense", "category_id": None, "memo": "x", "amount_minor": 1, "day_of_month": 1},  # inactive
    ])
    monkeypatch.setattr("app.repositories.tx_repo.recurring_ids_in_month", lambda uid, s, e: {"r3"})
    created = []
    monkeypatch.setattr(rs.tx_service, "create_transaction", lambda uid, p: created.append(p))

    assert rs.materialize_month("u", "2026-06") == 1
    assert created[0].occurred_on == date(2026, 6, 1)
    assert created[0].amount_minor == 500000
    assert created[0].parse_meta["recurring_id"] == "r1"


def test_materialize_clamps_day_to_month_end(monkeypatch):
    monkeypatch.setattr(rs, "today_kst", lambda: date(2026, 2, 28))
    _rules(monkeypatch, [
        {"id": "r1", "active": True, "direction": "expense", "category_id": None, "memo": "월세", "amount_minor": 500000, "day_of_month": 31},
    ])
    monkeypatch.setattr("app.repositories.tx_repo.recurring_ids_in_month", lambda uid, s, e: set())
    created = []
    monkeypatch.setattr(rs.tx_service, "create_transaction", lambda uid, p: created.append(p))

    rs.materialize_month("u", "2026-02")
    assert created[0].occurred_on == date(2026, 2, 28)  # 31 -> 28


def test_upcoming_fixed_sums_only_future_expense(monkeypatch):
    today = date(2026, 6, 10)
    _rules(monkeypatch, [
        {"id": "a", "active": True, "direction": "expense", "amount_minor": 500000, "day_of_month": 25},  # upcoming
        {"id": "b", "active": True, "direction": "expense", "amount_minor": 13500, "day_of_month": 5},  # past
        {"id": "c", "active": True, "direction": "income", "amount_minor": 99, "day_of_month": 25},  # income
        {"id": "d", "active": False, "direction": "expense", "amount_minor": 1, "day_of_month": 25},  # inactive
    ])
    # calendar window June
    assert rs.upcoming_fixed_minor("u", "2026-06-01", "2026-07-01", today) == 500000


def test_upcoming_fixed_in_cycle_window(monkeypatch):
    # pay cycle 6/10 ~ 7/9 (end exclusive 7/10), today 6/10: rule on the 5th fires
    # 7/5 (inside the cycle, after today) -> counted; rule on the 25th fires 6/25 -> counted.
    today = date(2026, 6, 10)
    _rules(monkeypatch, [
        {"id": "rent", "active": True, "direction": "expense", "amount_minor": 500000, "day_of_month": 25},  # 6/25
        {"id": "sub", "active": True, "direction": "expense", "amount_minor": 10000, "day_of_month": 5},  # 7/5
    ])
    assert rs.upcoming_fixed_minor("u", "2026-06-10", "2026-07-10", today) == 510000


def test_upcoming_fixed_clamped_cycle_counts_both_occurrences(monkeypatch):
    # payday 31 -> cycle [2/28, 3/31) is 31 days; a rule on the 28th fires BOTH
    # 2/28 and 3/28. On 2/28 the March one is still upcoming -> counted.
    today = date(2025, 2, 28)
    _rules(monkeypatch, [
        {"id": "x", "active": True, "direction": "expense", "amount_minor": 70000, "day_of_month": 28},
    ])
    assert rs.upcoming_fixed_minor("u", "2025-02-28", "2025-03-31", today) == 70000
