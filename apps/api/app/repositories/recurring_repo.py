from app.services.supabase import get_supabase, single_or_none

_TABLE = "recurring_rules"
_COLS = "id, category_id, amount_minor, direction, day_of_month, memo, active"


def list_rules(user_id: str) -> list[dict]:
    response = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .order("day_of_month")
        .execute()
    )
    return response.data or []


def get_rule(user_id: str, rule_id: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .eq("id", rule_id)
        .limit(1)
        .execute()
    )
    return single_or_none(response)


def create_rule(user_id: str, fields: dict) -> dict | None:
    response = get_supabase().table(_TABLE).insert({**fields, "user_id": user_id}).execute()
    return single_or_none(response)


def update_rule(user_id: str, rule_id: str, fields: dict) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .update(fields)
        .eq("user_id", user_id)
        .eq("id", rule_id)
        .execute()
    )
    return single_or_none(response)


def delete_rule(user_id: str, rule_id: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .delete()
        .eq("user_id", user_id)
        .eq("id", rule_id)
        .execute()
    )
    return single_or_none(response)
