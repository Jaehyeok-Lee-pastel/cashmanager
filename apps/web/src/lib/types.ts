export type Direction = "expense" | "income";
export type TxSource = "nl_text" | "manual" | "receipt" | "voice" | "import";
export type AmbiguousField = "amount" | "category" | "memo" | "date";

export interface Profile {
  id: string;
  email: string;
  display_name: string | null;
}

export interface Category {
  id: string;
  name: string;
  emoji: string | null;
  sort_order: number;
}

export interface Transaction {
  id: string;
  amount_minor: number;
  direction: Direction;
  category_id: string | null;
  memo: string | null;
  occurred_on: string; // YYYY-MM-DD
  source: TxSource;
  created_at: string;
}

export interface ParseResult {
  amount_minor: number | null;
  direction: Direction;
  category_id: string | null;
  category_name: string | null;
  memo: string | null;
  occurred_on: string | null;
  confidence: number;
  ambiguous_fields: AmbiguousField[];
  needs_manual: boolean;
  source: TxSource;
  raw_input: string;
  parse_meta: Record<string, unknown> | null;
}

export interface TransactionCreate {
  amount_minor: number;
  direction: Direction;
  category_id?: string | null;
  memo?: string | null;
  occurred_on?: string | null;
  source?: TxSource;
  raw_input?: string | null;
  parse_meta?: Record<string, unknown> | null;
}

export interface CategorySummary {
  category_id: string | null;
  name: string;
  emoji: string | null;
  sum_minor: number;
  ratio: number;
  limit_minor: number | null;
}

export interface Budget {
  category_id: string;
  limit_minor: number;
}

export interface BudgetSuggestion {
  category_id: string;
  name: string;
  suggested_minor: number;
}

export type InsightSeverity = "alert" | "warn" | "info";

export interface InsightCard {
  type: string;
  severity: InsightSeverity;
  title: string;
  detail: string;
}

export interface AssistantAnswer {
  answer: string;
}

export interface MonthlySummary {
  month: string;
  total_expense: number;
  total_income: number;
  count: number;
  by_category: CategorySummary[];
}
