import type { Transaction } from "./types";

export interface QuickChip {
  label: string;
  raw: string;
}

/** Most-used "memo + amount" combos for 1-tap re-entry. */
export function recentChips(transactions: Transaction[], limit = 5): QuickChip[] {
  const counts = new Map<string, { chip: QuickChip; count: number }>();
  for (const t of transactions) {
    if (!t.memo) continue;
    const key = `${t.memo}|${t.amount_minor}`;
    const existing = counts.get(key);
    if (existing) {
      existing.count += 1;
    } else {
      counts.set(key, {
        chip: {
          label: `${t.memo} ${t.amount_minor.toLocaleString("ko-KR")}`,
          raw: `${t.memo} ${t.amount_minor}`,
        },
        count: 1,
      });
    }
  }
  return [...counts.values()]
    .sort((a, b) => b.count - a.count)
    .slice(0, limit)
    .map((e) => e.chip);
}
