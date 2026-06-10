from app.services.supabase import get_supabase, single_or_none

_TABLE = "profiles"
_COLS = "id, email, display_name, pay_anchor_day"


def get_profile(user_id: str) -> dict | None:
    response = (
        get_supabase().table(_TABLE).select(_COLS).eq("id", user_id).limit(1).execute()
    )
    return single_or_none(response)


def update_profile(user_id: str, fields: dict) -> dict | None:
    if not fields:
        return get_profile(user_id)
    response = (
        get_supabase().table(_TABLE).update(fields).eq("id", user_id).execute()
    )
    return single_or_none(response)
