import type { Transaction } from "../../lib/types";

export interface DateGroup {
  date: string; // YYYY-MM-DD
  expenseSum: number; // total spent that day (expense only)
  items: Transaction[];
}

/** Group transactions by occurred_on, newest day first, items newest first. */
export function groupByDate(transactions: Transaction[]): DateGroup[] {
  const byDate = new Map<string, Transaction[]>();
  for (const t of transactions) {
    const arr = byDate.get(t.occurred_on);
    if (arr) arr.push(t);
    else byDate.set(t.occurred_on, [t]);
  }
  return [...byDate.entries()]
    .sort((a, b) => (a[0] < b[0] ? 1 : -1))
    .map(([date, items]) => ({
      date,
      expenseSum: items
        .filter((t) => t.direction === "expense")
        .reduce((s, t) => s + t.amount_minor, 0),
      items,
    }));
}
