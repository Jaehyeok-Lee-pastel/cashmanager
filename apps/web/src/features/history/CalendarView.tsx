import { useMemo } from "react";
import type { Transaction } from "../../lib/types";

const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];

interface Props {
  month: string; // "YYYY-MM"
  transactions: Transaction[];
  onPickDay: (date: string) => void;
}

/** Compact won for a tiny grid cell: 12000 -> "1.2만", 4900 -> "4,900". */
function compact(amount: number): string {
  if (amount >= 10000) {
    const man = amount / 10000;
    return `${Number.isInteger(man) ? man : man.toFixed(1)}만`;
  }
  return amount.toLocaleString("ko-KR");
}

/** Month grid of daily expense totals; tapping a day drills into it. */
export function CalendarView({ month, transactions, onPickDay }: Props) {
  const [year, mon] = month.split("-").map(Number);
  const firstWeekday = new Date(year, mon - 1, 1).getDay(); // 0=Sun
  const totalDays = new Date(year, mon, 0).getDate();

  // day-of-month -> expense sum (calendar is an unfiltered month overview)
  const sums = useMemo(() => {
    const acc: Record<number, number> = {};
    for (const t of transactions) {
      if (t.direction !== "expense" || !t.occurred_on.startsWith(month)) continue;
      const day = Number(t.occurred_on.slice(8, 10));
      acc[day] = (acc[day] ?? 0) + t.amount_minor;
    }
    return acc;
  }, [transactions, month]);

  const cells: (number | null)[] = [
    ...Array<null>(firstWeekday).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ];

  return (
    <div className="calendar">
      <div className="calendar-grid calendar-head" aria-hidden>
        {WEEKDAYS.map((w) => (
          <div key={w} className="cal-weekday">{w}</div>
        ))}
      </div>
      <div className="calendar-grid">
        {cells.map((day, i) => {
          if (day == null) return <div key={`b${i}`} className="cal-cell cal-blank" />;
          const spend = sums[day] ?? 0;
          const iso = `${month}-${String(day).padStart(2, "0")}`;
          return (
            <button
              key={iso}
              type="button"
              className={`cal-cell${spend > 0 ? " has-spend" : ""}`}
              aria-label={`${mon}월 ${day}일${spend > 0 ? `, 지출 ${spend.toLocaleString("ko-KR")}원` : ", 지출 없음"}`}
              onClick={() => onPickDay(iso)}
            >
              <span className="cal-day-num">{day}</span>
              {spend > 0 && <span className="cal-amount">{compact(spend)}</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}
