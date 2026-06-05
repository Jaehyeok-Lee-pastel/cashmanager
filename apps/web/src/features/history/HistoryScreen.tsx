import { useMemo, useState } from "react";
import { ErrorState, Spinner } from "../../components/states";
import { CategoryIcon } from "../../lib/categoryIcon";
import { colorForCategory, formatKRW, shiftMonth } from "../../lib/money";
import type { Transaction } from "../../lib/types";
import { useCategories } from "../categories/useCategories";
import { useTransactions } from "../ledger/useTransactions";
import { CalendarView } from "./CalendarView";
import { groupByDate } from "./groupByDate";

type ViewMode = "list" | "calendar";

type DirFilter = "all" | "expense" | "income";

const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];

function dateHeader(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const wd = WEEKDAYS[new Date(y, m - 1, d).getDay()];
  return `${m}월 ${d}일 (${wd})`;
}

interface Props {
  month: string;
  onMonthChange: (month: string) => void;
}

export function HistoryScreen({ month, onMonthChange }: Props) {
  const { categories } = useCategories();
  const { transactions, loading, error, reload } = useTransactions(month);

  const [query, setQuery] = useState("");
  const [dir, setDir] = useState<DirFilter>("all");
  const [catFilter, setCatFilter] = useState<Set<string>>(new Set());
  const [day, setDay] = useState(""); // "" = whole month, else "YYYY-MM-DD"
  const [view, setView] = useState<ViewMode>("list");

  const nameOf = (id: string | null) =>
    categories?.find((c) => c.id === id)?.name ?? "미분류";

  // picking a day in another month loads that month, then narrows to that day
  function pickDay(value: string) {
    setDay(value);
    if (value && value.slice(0, 7) !== month) onMonthChange(value.slice(0, 7));
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (transactions ?? []).filter((t) => {
      if (day && t.occurred_on !== day) return false;
      if (dir !== "all" && t.direction !== dir) return false;
      if (catFilter.size > 0 && !catFilter.has(t.category_id ?? "")) return false;
      if (q) {
        const hay = `${t.memo ?? ""} ${nameOf(t.category_id)}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [transactions, query, dir, catFilter, day, categories]);

  const groups = useMemo(() => groupByDate(filtered), [filtered]);
  const hasFilter =
    query.trim() !== "" || dir !== "all" || catFilter.size > 0 || day !== "";

  function toggleCat(id: string) {
    setCatFilter((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  return (
    <div className="history-screen">
      <div className="month-nav">
        <button type="button" aria-label="이전 달" onClick={() => onMonthChange(shiftMonth(month, -1))}>
          ‹
        </button>
        <strong>{month}</strong>
        <button type="button" aria-label="다음 달" onClick={() => onMonthChange(shiftMonth(month, 1))}>
          ›
        </button>
      </div>

      <div className="segmented view-toggle" role="group" aria-label="보기 방식">
        {(["list", "calendar"] as const).map((v) => (
          <button
            key={v}
            type="button"
            className={view === v ? "active" : ""}
            aria-pressed={view === v}
            onClick={() => setView(v)}
          >
            {v === "list" ? "리스트" : "달력"}
          </button>
        ))}
      </div>

      {view === "calendar" &&
        (loading ? (
          <Spinner rows={5} />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : (
          <CalendarView
            month={month}
            transactions={transactions ?? []}
            onPickDay={(d) => {
              pickDay(d);
              setView("list");
            }}
          />
        ))}

      {view === "list" && (
        <>
      <input
        className="history-search"
        type="search"
        aria-label="내역 검색"
        placeholder="메모·카테고리 검색"
        enterKeyHint="search"
        autoCapitalize="off"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <div className="day-filter">
        <input
          type="date"
          className="day-input"
          aria-label="일자 선택"
          value={day}
          onChange={(e) => pickDay(e.target.value)}
        />
        {day && (
          <button type="button" className="ghost" onClick={() => setDay("")}>
            전체 보기
          </button>
        )}
      </div>

      <div className="segmented" role="group" aria-label="유형 필터">
        {(["all", "expense", "income"] as const).map((d) => (
          <button
            key={d}
            type="button"
            className={dir === d ? "active" : ""}
            aria-pressed={dir === d}
            onClick={() => setDir(d)}
          >
            {d === "all" ? "전체" : d === "expense" ? "지출" : "수입"}
          </button>
        ))}
      </div>

      <div className="filter-chips">
        {(categories ?? []).map((c) => (
          <button
            key={c.id}
            type="button"
            className={`chip ${catFilter.has(c.id) ? "on" : ""}`}
            aria-pressed={catFilter.has(c.id)}
            onClick={() => toggleCat(c.id)}
          >
            {c.name}
          </button>
        ))}
      </div>

      {loading && <Spinner rows={5} />}
      {error && <ErrorState message={error} onRetry={reload} />}

      {!loading && !error && groups.length === 0 && (
        <div className="empty-state" aria-live="polite">
          <span className="emoji" aria-hidden>🔍</span>
          {hasFilter ? (
            <>
              <p className="title">조건에 맞는 거래가 없어요</p>
              <button
                type="button"
                className="ghost"
                onClick={() => {
                  setQuery("");
                  setDir("all");
                  setCatFilter(new Set());
                  setDay("");
                }}
              >
                필터 초기화
              </button>
            </>
          ) : (
            <p className="title">이 달엔 거래가 없어요</p>
          )}
        </div>
      )}

      {!loading && !error &&
        groups.map((g) => (
          <section key={g.date} className="date-group">
            <header className="date-head">
              <span>{dateHeader(g.date)}</span>
              <span className="tabular muted">-{formatKRW(g.expenseSum)}</span>
            </header>
            <ul className="tx-list">
              {g.items.map((tx) => (
                <HistoryRow key={tx.id} tx={tx} name={nameOf(tx.category_id)} />
              ))}
            </ul>
          </section>
        ))}
        </>
      )}
    </div>
  );
}

function HistoryRow({ tx, name }: { tx: Transaction; name: string }) {
  const color = colorForCategory(tx.category_id);
  return (
    <li className="tx-item">
      <span
        className="tx-chip"
        style={{ background: `color-mix(in srgb, ${color} 18%, transparent)` }}
      >
        <CategoryIcon name={name} color={color} />
      </span>
      <div className="tx-main">
        <span className="tx-memo">{tx.memo || name}</span>
        <span className="tx-sub">{name}</span>
      </div>
      <span className={`tx-amount ${tx.direction}`}>
        {tx.direction === "income" ? "+" : "-"}
        {formatKRW(tx.amount_minor)}
      </span>
    </li>
  );
}
