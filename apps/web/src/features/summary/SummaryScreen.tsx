import { useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { EmptyState, ErrorState, Spinner } from "../../components/states";
import { getMonthlySummary } from "../../lib/budget";
import { CategoryIcon } from "../../lib/categoryIcon";
import { formatKRW, shiftMonth } from "../../lib/money";
import type { CategorySummary, MonthlySummary } from "../../lib/types";
import { CHART_COLORS, CategoryChart } from "./CategoryChart";

interface Props {
  month: string;
  onMonthChange: (month: string) => void;
}

const MAX_SLICES = 6;

/** Keep the top categories; fold the rest into a single "기타" slice (3-7 rule). */
function groupCategories(items: CategorySummary[]): CategorySummary[] {
  if (items.length <= MAX_SLICES + 1) return items;
  const top = items.slice(0, MAX_SLICES);
  const rest = items.slice(MAX_SLICES);
  const restSum = rest.reduce((s, c) => s + c.sum_minor, 0);
  const restRatio = rest.reduce((s, c) => s + c.ratio, 0);
  return [
    ...top,
    {
      category_id: "__rest__",
      name: "기타",
      emoji: null,
      sum_minor: restSum,
      ratio: restRatio,
      limit_minor: null,
      projected_minor: null,
    },
  ];
}

export function SummaryScreen({ month, onMonthChange }: Props) {
  const token = useToken();
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getMonthlySummary(month, token)
      .then(setSummary)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "요약 불러오기 실패"),
      )
      .finally(() => setLoading(false));
  }, [month, token]);

  const grouped = summary ? groupCategories(summary.by_category) : [];
  const net = summary ? summary.total_income - summary.total_expense : 0;

  return (
    <div className="summary-screen">
      <div className="month-nav">
        <button type="button" aria-label="이전 달" onClick={() => onMonthChange(shiftMonth(month, -1))}>
          ‹
        </button>
        <strong>{month}</strong>
        <button type="button" aria-label="다음 달" onClick={() => onMonthChange(shiftMonth(month, 1))}>
          ›
        </button>
      </div>

      {loading && <Spinner rows={3} />}
      {error && <ErrorState message={error} />}

      {summary && !loading && !error && (
        <>
          {summary.daily_allowance != null && summary.safe_to_spend != null && (
            <div className="safe-card">
              {summary.safe_to_spend >= 0 ? (
                <>
                  <div className="safe-label">오늘 쓸 수 있어요</div>
                  <div className="safe-amount">{formatKRW(summary.daily_allowance)}</div>
                  <div className="safe-sub">
                    이번 달 남은 예산 {formatKRW(summary.safe_to_spend)}
                    {summary.upcoming_fixed_minor != null && (
                      <> · 고정비 {formatKRW(summary.upcoming_fixed_minor)} 차감</>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <div className="safe-label">이번 달 예산 초과</div>
                  <div className="safe-amount over">
                    {formatKRW(Math.abs(summary.safe_to_spend))} 초과
                  </div>
                </>
              )}
            </div>
          )}

          {grouped.length === 0 ? (
            <EmptyState emoji="📊" title="이 달은 조용하네요" message="아직 지출 기록이 없어요." />
          ) : (
            <>
              <div className="summary-caption">이번 달 지출</div>
              <div className="chart-wrap">
                <CategoryChart data={grouped} />
                <div className="chart-center">
                  <div className="amount">{formatKRW(summary.total_expense)}</div>
                </div>
              </div>
              {summary.projected_expense != null && (
                <div className="pace-line">
                  이 속도면 월말 예상 <strong>{formatKRW(summary.projected_expense)}</strong>
                </div>
              )}
            </>
          )}

          <div className="summary-stats">
            <div>
              <span className="label">수입</span>
              <strong className="income tabular">{formatKRW(summary.total_income)}</strong>
            </div>
            <div>
              <span className="label">잔액</span>
              <strong className={`tabular ${net >= 0 ? "income" : "negative"}`}>
                {net >= 0 ? "+" : "-"}
                {formatKRW(Math.abs(net))}
              </strong>
            </div>
          </div>

          {grouped.length > 0 && (
            <ul className="summary-breakdown">
              {grouped.map((c, i) => {
                const color = CHART_COLORS[i % CHART_COLORS.length];
                const hasBudget = c.limit_minor != null && c.limit_minor > 0;
                const budgetPct = hasBudget ? c.sum_minor / c.limit_minor! : null;
                const over = budgetPct != null && budgetPct >= 1;
                // on track to exceed but not over yet -> estimative badge
                const paceOver =
                  hasBudget &&
                  !over &&
                  c.projected_minor != null &&
                  c.projected_minor > c.limit_minor!;
                const barColor =
                  budgetPct == null
                    ? color
                    : over
                      ? "var(--color-error)"
                      : budgetPct >= 0.8
                        ? "var(--color-warn)"
                        : color;
                const barWidth =
                  budgetPct != null
                    ? Math.min(100, budgetPct * 100)
                    : Math.max(2, c.ratio * 100);
                return (
                  <li key={c.category_id ?? "none"}>
                    <div className="bd-head">
                      <span className="bd-name">
                        <span
                          className="bd-icon"
                          style={{ background: `color-mix(in srgb, ${color} 18%, transparent)` }}
                        >
                          <CategoryIcon name={c.name} size={15} color={color} />
                        </span>
                        {c.name}
                        {over && <span className="over-badge">초과</span>}
                        {paceOver && <span className="pace-badge">예상 초과</span>}
                      </span>
                      <span className="bd-value">
                        {hasBudget
                          ? `${formatKRW(c.sum_minor)} / ${formatKRW(c.limit_minor!)}`
                          : `${formatKRW(c.sum_minor)} · ${Math.round(c.ratio * 100)}%`}
                      </span>
                    </div>
                    <div className="bd-bar">
                      <div
                        className="bd-bar-fill"
                        style={{ width: `${barWidth}%`, background: barColor }}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
