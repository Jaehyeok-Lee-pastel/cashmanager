import logging

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.services.supabase import get_supabase

logger = logging.getLogger("cashmanager.health")
router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness — the process is up. Cheap, no external calls (for LB liveness)."""
    return {"ok": True, "service": settings.app_name}


@router.get("/ready")
def ready(response: Response) -> dict:
    """Readiness — can we actually serve traffic? Probes the DB so a load balancer
    can pull a dead instance instead of a static {ok:true} masking an outage."""
    db_ok = True
    try:
        get_supabase().table("categories").select("id").limit(1).execute()
    except Exception as exc:  # noqa: BLE001
        db_ok = False
        logger.warning("readiness DB probe failed: %s", exc)
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    # OpenAI is optional for the core ledger — reported but not gated on.
    return {"ready": db_ok, "db": db_ok, "openai_key": bool(settings.openai_api_key)}
