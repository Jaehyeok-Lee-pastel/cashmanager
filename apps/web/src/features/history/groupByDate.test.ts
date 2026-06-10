import { describe, expect, it } from "vitest";
import type { Transaction } from "../../lib/types";
import { groupByDate } from "./groupByDate";

const txs = [
  { id: "1", amount_minor: 5000, direction: "expense", category_id: null, memo: "a", occurred_on: "2026-06-02", source: "nl_text", created_at: "x" },
  { id: "2", amount_minor: 3000, direction: "income", category_id: null, memo: "b", occurred_on: "2026-06-02", source: "nl_text", created_at: "x" },
  { id: "3", amount_minor: 2000, direction: "expense", category_id: null, memo: "c", occurred_on: "2026-06-01", source: "nl_text", created_at: "x" },
] as Transaction[];

describe("groupByDate", () => {
  it("groups by day, newest first, and sums expenses only", () => {
    const groups = groupByDate(txs);
    expect(groups.map((g) => g.date)).toEqual(["2026-06-02", "2026-06-01"]);
    expect(groups[0].expenseSum).toBe(5000); // the 3000 income is excluded
    expect(groups[1].expenseSum).toBe(2000);
  });
});
