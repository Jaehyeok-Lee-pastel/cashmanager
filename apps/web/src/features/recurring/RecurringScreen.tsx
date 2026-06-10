import { useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { useSnackbar } from "../../app/SnackbarProvider";
import { ErrorState, Spinner } from "../../components/states";
import {
  createRecurring,
  deleteRecurring,
  getRecurring,
  materializeRecurring,
} from "../../lib/budget";
import { currentMonth, formatKRW } from "../../lib/money";
import type { RecurringRule } from "../../lib/types";
import { useCategories } from "../categories/useCategories";

export function RecurringScreen() {
  const token = useToken();
  const showSnackbar = useSnackbar();
  const { categories } = useCategories();
  const [rules, setRules] = useState<RecurringRule[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // add-form fields
  const [amount, setAmount] = useState("");
  const [day, setDay] = useState("1");
  const [categoryId, setCategoryId] = useState("");
  const [memo, setMemo] = useState("");

  function load() {
    setError(null);
    getRecurring(token)
      .then(setRules)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "불러오기 실패"));
  }
  useEffect(load, [token]);

  const nameOf = (id: string | null) =>
    categories?.find((c) => c.id === id)?.name ?? "미분류";

  async function add(e: React.FormEvent) {
    e.preventDefault();
    const won = Number(amount.replace(/[^\d]/g, ""));
    const d = Number(day);
    if (!won || won <= 0) return;
    setBusy(true);
    try {
      await createRecurring(
        {
          amount_minor: won,
          day_of_month: Math.min(31, Math.max(1, d)),
          category_id: categoryId || null,
          direction: "expense",
          memo: memo.trim() || null,
        },
        token,
      );
      setAmount("");
      setMemo("");
      load();
    } catch (err) {
      showSnackbar({ message: err instanceof Error ? err.message : "추가 실패" });
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    try {
      await deleteRecurring(id, token);
      load();
    } catch {
      showSnackbar({ message: "삭제에 실패했어요" });
    }
  }

  async function applyThisMonth() {
    setBusy(true);
    try {
      const { created } = await materializeRecurring(currentMonth(), token);
      showSnackbar({
        message: created > 0 ? `이번 달 고정지출 ${created}건을 넣었어요` : "이미 다 반영돼 있어요",
      });
    } catch (err) {
      showSnackbar({ message: err instanceof Error ? err.message : "반영 실패" });
    } finally {
      setBusy(false);
    }
  }

  if (!rules && !error) return <Spinner rows={4} />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="recurring-screen">
      <h2>고정지출</h2>
      <p className="muted">
        월세·구독처럼 매달 나가는 돈을 등록하면, 지난 날짜분은 한 번에 넣고
        아직 안 나간 분은 "오늘 쓸 수 있는 돈"에서 미리 빼드려요.
      </p>

      <form className="recurring-form" onSubmit={add}>
        <input
          type="text"
          inputMode="numeric"
          className="budget-input"
          aria-label="금액"
          placeholder="금액(원)"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <select aria-label="매월 며칠" value={day} onChange={(e) => setDay(e.target.value)}>
          {Array.from({ length: 31 }, (_, i) => i + 1).map((n) => (
            <option key={n} value={n}>매월 {n}일</option>
          ))}
        </select>
        <select aria-label="카테고리" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">미분류</option>
          {(categories ?? []).map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <input
          type="text"
          aria-label="메모"
          placeholder="메모 (예: 월세)"
          maxLength={40}
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
        />
        <button type="submit" disabled={busy || !amount.trim()}>추가</button>
      </form>

      <ul className="recurring-list">
        {(rules ?? []).map((r) => (
          <li key={r.id} className="recurring-row">
            <span className="rec-day">매월 {r.day_of_month}일</span>
            <span className="rec-main">
              {r.memo || nameOf(r.category_id)} · {nameOf(r.category_id)}
            </span>
            <span className="rec-amount tabular">{formatKRW(r.amount_minor)}</span>
            <button type="button" className="icon-btn" aria-label="삭제" onClick={() => remove(r.id)}>
              ×
            </button>
          </li>
        ))}
        {rules && rules.length === 0 && <li className="muted">아직 등록한 고정지출이 없어요.</li>}
      </ul>

      <button type="button" onClick={applyThisMonth} disabled={busy || (rules?.length ?? 0) === 0}>
        이번 달 고정지출 넣기
      </button>
    </div>
  );
}
