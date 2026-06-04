import type { Category, Transaction } from "./types";
import { todayKST } from "./money";

const HEADERS = ["날짜", "유형", "카테고리", "금액(원)", "메모"];

/** Quote a CSV field and escape embedded quotes (RFC 4180). */
function cell(value: string): string {
  return `"${value.replace(/"/g, '""')}"`;
}

/** Build a spreadsheet-friendly CSV from transactions (newest first). */
export function transactionsToCsv(
  transactions: Transaction[],
  categories: Category[],
): string {
  const nameOf = new Map(categories.map((c) => [c.id, c.name]));
  const rows = transactions.map((t) =>
    [
      t.occurred_on,
      t.direction === "income" ? "수입" : "지출",
      t.category_id ? nameOf.get(t.category_id) ?? "미분류" : "미분류",
      String(t.amount_minor),
      t.memo ?? "",
    ]
      .map(cell)
      .join(","),
  );
  // BOM (﻿) so Excel reads the Korean text as UTF-8.
  return "﻿" + [HEADERS.map(cell).join(","), ...rows].join("\r\n");
}

/** Trigger a browser download of the given text as a file. */
export function downloadCsv(content: string, filename: string): void {
  const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/** Default export filename, e.g. "cashmanager-2026-06-05.csv". */
export function exportFilename(): string {
  return `cashmanager-${todayKST()}.csv`;
}
