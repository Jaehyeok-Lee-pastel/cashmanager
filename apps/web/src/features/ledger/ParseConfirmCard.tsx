import { useEffect, useRef, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { createTransaction } from "../../lib/budget";
import { formatKRW, todayKST } from "../../lib/money";
import type {
  AmbiguousField,
  Category,
  Direction,
  ParseResult,
  Transaction,
} from "../../lib/types";

interface Props {
  result: ParseResult;
  categories: Category[];
  onSaved: (tx: Transaction) => void;
  onCancel: () => void;
}

export function ParseConfirmCard({ result, categories, onSaved, onCancel }: Props) {
  const token = useToken();
  const [amount, setAmount] = useState<string>(
    result.amount_minor != null ? String(result.amount_minor) : "",
  );
  const [categoryId, setCategoryId] = useState<string>(result.category_id ?? "");
  const [direction, setDirection] = useState<Direction>(result.direction);
  const [memo, setMemo] = useState<string>(result.memo ?? "");
  const [date, setDate] = useState<string>(result.occurred_on ?? todayKST());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const amountRef = useRef<HTMLInputElement>(null);

  // move focus into the card when it appears so keyboard/screen-reader users
  // land on it instead of staying on the input bar below.
  useEffect(() => {
    amountRef.current?.focus();
  }, []);

  const isAmbiguous = (f: AmbiguousField) => result.ambiguous_fields.includes(f);
  const highConfidence = result.confidence >= 0.8 && !result.needs_manual;

  async function save() {
    const amountValue = Number(amount);
    if (!amountValue || amountValue <= 0) {
      setError("금액을 입력해주세요.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const tx = await createTransaction(
        {
          amount_minor: amountValue,
          direction,
          category_id: categoryId || null,
          memo: memo || null,
          occurred_on: date,
          source: result.source,
          raw_input: result.raw_input,
          parse_meta: {
            ...(result.parse_meta ?? {}),
            corrected: categoryId !== (result.category_id ?? ""),
          },
        },
        token,
      );
      onSaved(tx);
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  const amountNum = Number(amount);
  const saveLabel =
    amountNum > 0 ? `${formatKRW(amountNum)} 기록하기` : "기록하기";

  return (
    <div
      className={`confirm-card ${highConfidence ? "confident" : "low"}`}
      role="group"
      aria-label="거래 확인"
    >
      {highConfidence ? (
        <span className="confidence-badge high">✓ 확실</span>
      ) : (
        <span className="confidence-badge low">⚠ AI 추정 — 확인해주세요</span>
      )}
      {result.needs_manual && (
        <p className="muted">AI 분석이 어려워요. 직접 확인해주세요.</p>
      )}

      <div className="field">
        <label htmlFor="cc-amount">금액</label>
        <input
          ref={amountRef}
          id="cc-amount"
          type="text"
          inputMode="decimal"
          className={isAmbiguous("amount") ? "ambiguous" : ""}
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="cc-category">카테고리</label>
        <select
          id="cc-category"
          className={isAmbiguous("category") ? "ambiguous" : ""}
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
        >
          <option value="">미분류</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.emoji ? `${c.emoji} ` : ""}
              {c.name}
            </option>
          ))}
        </select>
        {isAmbiguous("category") && (
          <p className="field-hint">⚠ 카테고리를 추측했어요 — 맞는지 확인해주세요</p>
        )}
      </div>

      <div className="field">
        <label htmlFor="cc-memo">메모</label>
        <input
          id="cc-memo"
          type="text"
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
        />
      </div>

      <div className="field row">
        <div>
          <label htmlFor="cc-date">날짜</label>
          <input
            id="cc-date"
            type="date"
            className={isAmbiguous("date") ? "ambiguous" : ""}
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="cc-dir">유형</label>
          <select
            id="cc-dir"
            value={direction}
            onChange={(e) => setDirection(e.target.value as Direction)}
          >
            <option value="expense">지출</option>
            <option value="income">수입</option>
            <option value="transfer">이체</option>
          </select>
        </div>
      </div>

      {error && <p className="status status-error" role="alert">{error}</p>}

      <div className="actions">
        <button type="button" className="ghost" onClick={onCancel} disabled={busy}>
          취소
        </button>
        <button type="button" className="primary-grad" onClick={save} disabled={busy}>
          {busy ? "저장 중…" : saveLabel}
        </button>
      </div>
    </div>
  );
}
