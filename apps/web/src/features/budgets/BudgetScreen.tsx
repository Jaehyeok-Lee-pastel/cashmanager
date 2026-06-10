import { useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { ErrorState, Spinner } from "../../components/states";
import {
  deleteBudget,
  getBudgetSuggestions,
  getBudgetTemplate,
  upsertBudgets,
} from "../../lib/budget";
import { CategoryIcon } from "../../lib/categoryIcon";
import { colorForCategory } from "../../lib/money";
import type { Budget } from "../../lib/types";
import { useCategories } from "../categories/useCategories";
import { useBudgets } from "./useBudgets";

export function BudgetScreen() {
  const token = useToken();
  const { categories } = useCategories();
  const { budgets, loading, error, reload } = useBudgets();

  // categoryId -> limit string (empty = no budget)
  const [limits, setLimits] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [income, setIncome] = useState("");
  const [invest, setInvest] = useState("");

  useEffect(() => {
    if (budgets) {
      setLimits(Object.fromEntries(budgets.map((b) => [b.category_id, String(b.limit_minor)])));
    }
  }, [budgets]);

  async function applySuggestions() {
    setNotice(null);
    try {
      const suggestions = await getBudgetSuggestions(token);
      setLimits((prev) => {
        const next = { ...prev };
        for (const s of suggestions) next[s.category_id] = String(s.suggested_minor);
        return next;
      });
      setNotice("최근 3개월 평균으로 채웠어요. 확인 후 저장하세요.");
    } catch {
      setNotice("자동 제안을 불러오지 못했어요.");
    }
  }

  // cold start (no 3-month history yet): draft a budget from income − investment.
  async function applyTemplate() {
    const won = Number(income.replace(/[^\d]/g, ""));
    const investWon = Number(invest.replace(/[^\d]/g, "")) || 0;
    if (!won || won <= 0) {
      setNotice("월 실수령액을 입력해주세요.");
      return;
    }
    if (investWon >= won) {
      setNotice("투자/저축이 소득보다 크거나 같아요. 다시 확인해주세요.");
      return;
    }
    setNotice(null);
    try {
      const suggestions = await getBudgetTemplate(won, investWon, token);
      if (suggestions.length === 0) {
        setNotice("초안을 만들 카테고리가 없어요.");
        return;
      }
      setLimits((prev) => {
        const next = { ...prev };
        for (const s of suggestions) next[s.category_id] = String(s.suggested_minor);
        return next;
      });
      const consume = won - (investWon || Math.round(won * 0.3));
      setNotice(`소비예산 ${consume.toLocaleString("ko-KR")}원으로 초안을 만들었어요. 확인 후 저장하세요.`);
    } catch {
      setNotice("초안을 만들지 못했어요.");
    }
  }

  async function save() {
    setBusy(true);
    setNotice(null);
    try {
      const toUpsert: Budget[] = [];
      const toDelete: string[] = [];
      for (const c of categories ?? []) {
        const raw = (limits[c.id] ?? "").trim();
        const value = Number(raw);
        if (raw && value > 0) toUpsert.push({ category_id: c.id, limit_minor: value });
        else if (budgets?.some((b) => b.category_id === c.id)) toDelete.push(c.id);
      }
      if (toUpsert.length) await upsertBudgets(toUpsert, token);
      await Promise.all(toDelete.map((id) => deleteBudget(id, token)));
      reload();
      setNotice("저장했어요.");
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "저장 실패");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Spinner rows={4} />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  return (
    <div className="budget-screen">
      <h2>월 예산</h2>
      <p className="muted">카테고리별 한 달 한도를 정하면 요약에서 진행률을 볼 수 있어요.</p>

      <button type="button" className="ghost" onClick={applySuggestions} disabled={busy}>
        최근 3개월 평균으로 자동 채우기
      </button>

      <details className="budget-onboarding">
        <summary>처음이신가요? 소득으로 예산 초안 만들기</summary>
        <p className="onboard-note">
          소득에서 <strong>월 투자/저축</strong>을 빼고 남은 돈으로 소비예산 초안을
          만들어요. 주거비·통신비·카드대금은 직접 넣어주세요. 언제든 수정·저장 가능해요.
        </p>
        <div className="onboard-row">
          <input
            type="text"
            inputMode="numeric"
            className="budget-input"
            aria-label="월 실수령액"
            placeholder="월 실수령액 (원)"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
          />
          <input
            type="text"
            inputMode="numeric"
            className="budget-input"
            aria-label="월 투자·저축 (선택)"
            placeholder="월 투자·저축 (선택)"
            value={invest}
            onChange={(e) => setInvest(e.target.value)}
          />
          <button type="button" className="ghost" onClick={applyTemplate} disabled={busy}>
            초안 만들기
          </button>
        </div>
      </details>

      {notice && <p className="status" role="status">{notice}</p>}

      <ul className="budget-list">
        {(categories ?? []).map((c) => {
          const color = colorForCategory(c.id);
          return (
            <li key={c.id} className="budget-row">
              <span className="bd-name">
                <span
                  className="bd-icon"
                  style={{ background: `color-mix(in srgb, ${color} 18%, transparent)` }}
                >
                  <CategoryIcon name={c.name} size={15} color={color} />
                </span>
                {c.name}
              </span>
              <input
                type="text"
                inputMode="decimal"
                className="budget-input"
                aria-label={`${c.name} 예산`}
                placeholder="없음"
                value={limits[c.id] ?? ""}
                onChange={(e) => setLimits((p) => ({ ...p, [c.id]: e.target.value }))}
              />
            </li>
          );
        })}
      </ul>

      <button type="button" onClick={save} disabled={busy}>
        {busy ? "저장 중…" : "예산 저장"}
      </button>
    </div>
  );
}
