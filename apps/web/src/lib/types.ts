export type Direction = "expense" | "income" | "transfer";
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
  projected_minor: number | null; // month-end pace projection (null = N/A)
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

export interface RecurringRule {
  id: string;
  category_id: string | null;
  amount_minor: number;
  direction: Direction;
  day_of_month: number;
  memo: string | null;
  active: boolean;
}

export interface RecurringCreate {
  category_id: string | null;
  amount_minor: number;
  direction: Direction;
  day_of_month: number;
  memo: string | null;
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
  projected_expense: number | null; // projected month-end total (null = N/A)
  budget_total: number | null; // sum of category budgets (null = none set)
  safe_to_spend: number | null; // remaining budget this month (may be negative)
  daily_allowance: number | null; // today's per-day allowance (null = N/A)
  upcoming_fixed_minor: number | null; // fixed costs still due this month
  invested_minor: number | null; // moved into investments this month
}
