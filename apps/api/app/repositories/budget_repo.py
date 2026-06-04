from app.core.timeutils import datetime_now_iso
from app.services.supabase import get_supabase

_TABLE = "category_budgets"


def list_budgets(user_id: str) -> list[dict]:
    response = (
        get_supabase()
        .table(_TABLE)
        .select("category_id, limit_minor")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


def upsert_budget(user_id: str, category_id: str, limit_minor: int) -> None:
    payload = {
        "user_id": user_id,
        "category_id": category_id,
        "limit_minor": limit_minor,
        "updated_at": datetime_now_iso(),
    }
    get_supabase().table(_TABLE).upsert(
        payload, on_conflict="user_id,category_id"
    ).execute()


def delete_budget(user_id: str, category_id: str) -> None:
    (
        get_supabase()
        .table(_TABLE)
        .delete()
        .eq("user_id", user_id)
        .eq("category_id", category_id)
        .execute()
    )
