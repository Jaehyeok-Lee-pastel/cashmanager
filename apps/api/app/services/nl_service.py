"""Orchestrates natural-language parsing: preprocess -> fast-path or LLM -> map.

Always returns a ParseResult (never raises to the caller). On any LLM failure
it degrades to a manual-entry preview (needs_manual=True) with the amount
filled from regex — there is no dead end.
"""

import logging
from datetime import date

from app.core.timeutils import today_kst
from app.repositories import category_repo, merchant_map_repo
from app.schemas.nl import ParseResult
from app.services import hangul, merchant_norm, nl_preprocess, openai_service

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.8
# NOTE: "정산" is intentionally excluded — it's ambiguous (정산금 받음=income vs
# 정산금 냄=expense), so we let the LLM decide rather than force income.
_INCOME_HINTS = ("월급", "급여", "입금", "환급", "수입", "용돈")
_FALLBACK_CATEGORY = "기타지출"


def parse(user_id: str, text: str) -> ParseResult:
    """Public entry: repair typos (NFC + broken-jamo) before parsing, but keep
    the user's ORIGINAL text as raw_input so nothing is silently rewritten."""
    cleaned = hangul.clean(text)
    result = _parse(user_id, cleaned)
    updates: dict = {}
    # standardize the memo (expand brand aliases, drop filler/amount tokens);
    # keep the original if normalization would empty it.
    norm_memo = merchant_norm.normalize_memo(result.memo or "")
    if norm_memo and norm_memo != result.memo:
        updates["memo"] = norm_memo
    if cleaned != text:
        updates["raw_input"] = text
        updates["parse_meta"] = {**(result.parse_meta or {}), "corrected_from": text}
    return result.model_copy(update=updates) if updates else result


def _parse(user_id: str, text: str) -> ParseResult:
    today = today_kst()
    categories = category_repo.list_categories(user_id)
    name_to_id = {_norm(c["name"]): c["id"] for c in categories}
    id_to_name = {c["id"]: c["name"] for c in categories}
    category_names = [c["name"] for c in categories]

    occurred_on, remainder = nl_preprocess.parse_date(text, today)
    amount = nl_preprocess.parse_amount(remainder)

    # 0) credit-card bill payment -> transfer (not spending). Recording it as an
    #    expense would double-count the individual card purchases already logged.
    if amount is not None and nl_preprocess.is_card_payment(text):
        return _transfer_result(text, amount, occurred_on or today, name_to_id)

    # 1) learned merchant map — instant, free, deterministic (improves with use)
    keyword = nl_preprocess.merchant_keyword(text)
    if keyword and amount is not None:
        learned_id = merchant_map_repo.get_category_id(user_id, keyword)
        if learned_id and learned_id in id_to_name:
            return _map_result(
                text, amount, occurred_on or today, learned_id, id_to_name[learned_id]
            )

    # 2) pure-number fast-path (no categorization signal -> skip LLM)
    if _can_fast_path(text, amount):
        return _fast_path_result(text, amount, occurred_on or today)

    try:
        parsed = openai_service.parse_line(
            text, category_names, today, known_amount=amount, known_date=occurred_on
        )
    except Exception as exc:  # noqa: BLE001 — any LLM failure -> manual fallback
        logger.warning("LLM parse failed, falling back to manual: %s", exc)
        return _manual_fallback(text, amount, occurred_on or today)

    return _build_result(text, parsed, name_to_id, occurred_on, amount, today)


def _norm(name: str) -> str:
    return name.strip().lower()


def _can_fast_path(text: str, amount: int | None) -> bool:
    if amount is None:
        return False
    if any(hint in text for hint in _INCOME_HINTS):
        return False
    return nl_preprocess.is_trivial(text)


def _meta(route: str, confidence: float, parsed_category_name: str | None,
          model: str | None = None, latency_ms: int | None = None) -> dict:
    """Consistent parse_meta shape across every code path (matches the DB doc)."""
    return {
        "route": route,
        "confidence": confidence,
        "model": model,
        "latency_ms": latency_ms,
        "parsed_category_name": parsed_category_name,
        "corrected": False,
    }


def _map_result(
    text: str, amount: int, occurred_on: date, category_id: str, category_name: str
) -> ParseResult:
    direction = (
        "income"
        if category_name == "수입" or any(h in text for h in _INCOME_HINTS)
        else "expense"
    )
    return ParseResult(
        amount_minor=amount,
        direction=direction,
        category_id=category_id,
        category_name=category_name,
        memo=text.strip(),
        occurred_on=occurred_on,
        confidence=0.95,
        ambiguous_fields=[],
        needs_manual=False,
        source="nl_text",
        raw_input=text,
        parse_meta=_meta("merchant_map", 0.95, category_name),
    )


_CARD_BILL_CATEGORY = "카드대금"


def _transfer_result(
    text: str, amount: int, occurred_on: date, name_to_id: dict[str, str]
) -> ParseResult:
    """A credit-card bill payment: a transfer, excluded from spending totals."""
    cid = name_to_id.get(_norm(_CARD_BILL_CATEGORY))
    return ParseResult(
        amount_minor=amount,
        direction="transfer",
        category_id=cid,
        category_name=_CARD_BILL_CATEGORY if cid else None,
        memo=text.strip(),
        occurred_on=occurred_on,
        confidence=0.9,
        ambiguous_fields=[],
        needs_manual=False,
        source="nl_text",
        raw_input=text,
        parse_meta=_meta("card_payment", 0.9, _CARD_BILL_CATEGORY if cid else None),
    )


def _fast_path_result(text: str, amount: int, occurred_on: date) -> ParseResult:
    return ParseResult(
        amount_minor=amount,
        direction="expense",
        category_id=None,
        category_name=None,
        memo=text.strip(),
        occurred_on=occurred_on,
        confidence=0.5,
        ambiguous_fields=["category"],
        needs_manual=False,
        source="nl_text",
        raw_input=text,
        parse_meta=_meta("fast_path", 0.5, None),
    )


def _manual_fallback(text: str, amount: int | None, occurred_on: date) -> ParseResult:
    fields: list = ["category"]
    if amount is None:
        fields.insert(0, "amount")
    return ParseResult(
        amount_minor=amount,
        direction="expense",
        category_id=None,
        category_name=None,
        memo=text.strip(),
        occurred_on=occurred_on,
        confidence=0.0,
        ambiguous_fields=fields,
        needs_manual=True,
        source="manual",  # LLM failed; user will enter/confirm manually
        raw_input=text,
        parse_meta=_meta("manual_fallback", 0.0, None),
    )


def _build_result(
    text: str,
    parsed: dict,
    name_to_id: dict[str, str],
    pre_date: date | None,
    pre_amount: int | None,
    today: date,
) -> ParseResult:
    category_name = parsed.get("category") or _FALLBACK_CATEGORY
    category_id = name_to_id.get(_norm(category_name))

    confidence = float(parsed.get("confidence", 0.0))
    ambiguous: list = []
    if category_id is None or confidence < CONFIDENCE_THRESHOLD:
        ambiguous.append("category")

    occurred_on = pre_date or _coerce_date(parsed.get("occurred_on"), today)
    amount = pre_amount if pre_amount is not None else parsed.get("amount")
    if not amount:  # None or 0 (the LLM can return 0 for the required integer field)
        ambiguous.insert(0, "amount")

    return ParseResult(
        amount_minor=amount,
        direction=parsed.get("direction", "expense"),
        category_id=category_id,
        category_name=category_name,
        memo=parsed.get("memo") or text.strip(),
        occurred_on=occurred_on,
        confidence=confidence,
        ambiguous_fields=ambiguous,
        needs_manual=False,
        source="nl_text",
        raw_input=text,
        parse_meta=_meta(
            "llm", confidence, category_name,
            model=parsed.get("model"), latency_ms=parsed.get("latency_ms"),
        ),
    )


def _coerce_date(value: str | None, today: date) -> date:
    if not value:
        return today
    try:
        return date.fromisoformat(value)
    except ValueError:
        return today
