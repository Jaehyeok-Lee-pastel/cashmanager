from app.core.timeutils import datetime_now_iso
from app.services.supabase import get_supabase, single_or_none

_TABLE = "merchant_category_map"


def get_category_id(user_id: str, keyword: str) -> str | None:
    response = (
        get_supabase()
        .table(_TABLE)
        .select("category_id")
        .eq("user_id", user_id)
        .eq("keyword", keyword)
        .limit(1)
        .execute()
    )
    row = single_or_none(response)
    return row["category_id"] if row else None


def upsert(user_id: str, keyword: str, category_id: str) -> None:
    """Learn (or correct) a merchant -> category mapping for this user."""
    payload = {
        "user_id": user_id,
        "keyword": keyword,
        "category_id": category_id,
        "updated_at": datetime_now_iso(),
    }
    get_supabase().table(_TABLE).upsert(
        payload, on_conflict="user_id,keyword"
    ).execute()
