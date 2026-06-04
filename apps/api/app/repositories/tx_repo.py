from app.services.supabase import get_supabase, single_or_none

_TABLE = "transactions"
_COLS = "id, amount_minor, direction, category_id, memo, occurred_on, source, created_at"


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


def list_for_summary(user_id: str, month_start: str, month_end: str) -> list[dict]:
    response = (
        get_supabase()
        .table(_TABLE)
        .select("amount_minor, direction, category_id")
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
