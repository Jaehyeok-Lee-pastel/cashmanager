from app.services.supabase import get_supabase, single_or_none

_TABLE = "categories"
_COLS = "id, name, emoji, sort_order"


def list_categories(user_id: str) -> list[dict]:
    response = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .is_("archived_at", "null")
        .order("sort_order")
        .execute()
    )
    return response.data or []


def get_category(user_id: str, category_id: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .select(_COLS)
        .eq("user_id", user_id)
        .eq("id", category_id)
        .limit(1)
        .execute()
    )
    return single_or_none(response)


def create_category(user_id: str, fields: dict) -> dict | None:
    payload = {**fields, "user_id": user_id}
    response = get_supabase().table(_TABLE).insert(payload).execute()
    return single_or_none(response)


def update_category(user_id: str, category_id: str, fields: dict) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .update(fields)
        .eq("user_id", user_id)
        .eq("id", category_id)
        .execute()
    )
    return single_or_none(response)


def archive_category(user_id: str, category_id: str, archived_at: str) -> dict | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .update({"archived_at": archived_at})
        .eq("user_id", user_id)
        .eq("id", category_id)
        .execute()
    )
    return single_or_none(response)
