import { describe, expect, it } from "vitest";
import type { Category, Transaction } from "./types";
import { transactionsToCsv } from "./exportCsv";

const cats = [{ id: "c1", name: "식비", emoji: null }] as Category[];
const txs = [
  {
    id: "t1", amount_minor: 8000, direction: "expense", category_id: "c1",
    memo: "김밥", occurred_on: "2026-06-01", source: "nl_text", created_at: "x",
  },
] as Transaction[];

describe("transactionsToCsv", () => {
  it("starts with a UTF-8 BOM (Excel-friendly)", () => {
    expect(transactionsToCsv(txs, cats).startsWith("﻿")).toBe(true);
  });

  it("includes header + the category name, amount and direction label", () => {
    const csv = transactionsToCsv(txs, cats);
    expect(csv).toContain("날짜");
    expect(csv).toContain("식비");
    expect(csv).toContain("8000");
    expect(csv).toContain("지출");
  });

  it("labels income rows and falls back to 미분류", () => {
    const income = [
      { ...txs[0], id: "t2", direction: "income", category_id: null },
    ] as Transaction[];
    const csv = transactionsToCsv(income, cats);
    expect(csv).toContain("수입");
    expect(csv).toContain("미분류");
  });
});
