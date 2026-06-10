from app.services.supabase import get_supabase, single_or_none

_TABLE = "transactions"
_COLS = "id, amount_minor, direction, category_id, memo, occurred_on, source, created_at, raw_input"


def list_transactions(
    user_id: str,
    month_start: str,
    month_end: str,
    category_id: str | None = None,
    limit: int = 200,
) -> list[dict]:
    query = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .gte("occurred_on", month_start)
        .lt("occurred_on", month_end)
    )
    if category_id:
        query = query.eq("category_id", category_id)
    response = query.order("occurred_on", desc=True).limit(limit).execute()
    return response.data or []


_EXPORT_PAGE = 1000


def list_all(user_id: str) -> list[dict]:
    """Every transaction for the user, newest first (for full data export/backup).

    Pages past PostgREST's default 1000-row cap so long histories export whole.
    """
    rows: list[dict] = []
    start = 0
    while True:
        response = (
            get_supabase()
            .table(_TABLE)
            .select(_COLS)
            .eq("user_id", user_id)
            .order("occurred_on", desc=True)
            .range(start, start + _EXPORT_PAGE - 1)
            .execute()
        )
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < _EXPORT_PAGE:
            return rows
        start += _EXPORT_PAGE


def recurring_ids_in_month(user_id: str, month_start: str, month_end: str) -> set[str]:
    """recurring_rule ids already materialized into transactions this month."""
    response = (
        get_supabase()
        .table(_TABLE)
        .select("parse_meta")
        .eq("user_id", user_id)
        .gte("occurred_on", month_start)
        .lt("occurred_on", month_end)
        .execute()
    )
    ids: set[str] = set()
    for row in response.data or []:
        rid = (row.get("parse_meta") or {}).get("recurring_id")
        if rid:
            ids.add(rid)
    return ids


def list_for_summary(user_id: str, month_start: str, month_end: str) -> list[dict]:
    response = (
        get_supabase()
        .table(_TABLE)
        .select("amount_minor, direction, category_id, parse_meta")
        .eq("user_id", user_id)
        .gte("occurred_on", month_start)
        .lt("occurred_on", month_end)
        .execute()
    )
    return response.data or []


def get_transaction(user_id: str, tx_id: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .eq("id", tx_id)
        .limit(1)
        .execute()
    )
    return single_or_none(response)


def create_transaction(user_id: str, fields: dict) -> dict | None:
    payload = {**fields, "user_id": user_id}
    response = get_supabase().table(_TABLE).insert(payload).execute()
    return single_or_none(response)


def update_transaction(user_id: str, tx_id: str, fields: dict) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .update(fields)
        .eq("user_id", user_id)
        .eq("id", tx_id)
        .execute()
    )
    return single_or_none(response)


def delete_transaction(user_id: str, tx_id: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .delete()
        .eq("user_id", user_id)
        .eq("id", tx_id)
        .execute()
    )
    return single_or_none(response)
