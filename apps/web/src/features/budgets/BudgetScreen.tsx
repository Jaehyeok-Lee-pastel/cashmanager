import { useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { ErrorState, Spinner } from "../../components/states";
import { deleteBudget, getBudgetSuggestions, upsertBudgets } from "../../lib/budget";
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
      {notice && <p className="status">{notice}</p>}

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
