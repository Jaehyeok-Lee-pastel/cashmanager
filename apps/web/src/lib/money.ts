/** Format KRW integer won for display, e.g. 4900 -> "4,900원". */
export function formatKRW(amountMinor: number): string {
  return `${amountMinor.toLocaleString("ko-KR")}원`;
}

/** Deterministically map a category id to one of the 8 palette tokens (--cat-1..8). */
export function colorForCategory(id: string | null): string {
  if (!id) return "var(--color-text-3)";
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  }
  return `var(--cat-${(hash % 8) + 1})`;
}

/** Current month as "YYYY-MM" in KST. */
export function currentMonth(): string {
  const now = new Date();
  const kst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60_000);
  return `${kst.getFullYear()}-${String(kst.getMonth() + 1).padStart(2, "0")}`;
}

/** Shift a "YYYY-MM" month by delta months. */
export function shiftMonth(month: string, delta: number): string {
  const [year, mon] = month.split("-").map(Number);
  const d = new Date(year, mon - 1 + delta, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}
