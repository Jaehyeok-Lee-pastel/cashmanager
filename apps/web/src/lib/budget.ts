import { apiDelete, apiGet, apiPatch, apiPost, apiPut } from "./api";
import type {
  AssistantAnswer,
  Budget,
  BudgetSuggestion,
  Category,
  InsightCard,
  MonthlySummary,
  ParseResult,
  Profile,
  Transaction,
  TransactionCreate,
} from "./types";

// --- Profile ---
export const getMe = (token: string) => apiGet<Profile>("/me", token);
export const updateMe = (displayName: string, token: string) =>
  apiPatch<Profile>("/me", { display_name: displayName }, token);

// --- Categories ---
export const listCategories = (token: string) =>
  apiGet<Category[]>("/categories", token);
export const createCategory = (name: string, emoji: string | null, token: string) =>
  apiPost<Category>("/categories", { name, emoji }, token);
export const updateCategory = (
  id: string,
  fields: Partial<Pick<Category, "name" | "emoji" | "sort_order">>,
  token: string,
) => apiPatch<Category>(`/categories/${id}`, fields, token);
export const archiveCategory = (id: string, token: string) =>
  apiDelete(`/categories/${id}`, token);

// --- Natural-language parse (preview only) ---
export const parseLine = (text: string, token: string) =>
  apiPost<ParseResult>("/transactions/parse", { text }, token);

// --- Transactions ---
export const listTransactions = (month: string, token: string) =>
  apiGet<Transaction[]>(`/transactions?month=${month}`, token);
export const createTransaction = (payload: TransactionCreate, token: string) =>
  apiPost<Transaction>("/transactions", payload, token);
export const updateTransaction = (
  id: string,
  payload: Partial<TransactionCreate>,
  token: string,
) => apiPatch<Transaction>(`/transactions/${id}`, payload, token);
export const deleteTransaction = (id: string, token: string) =>
  apiDelete(`/transactions/${id}`, token);

// --- Summary ---
export const getMonthlySummary = (month: string, token: string) =>
  apiGet<MonthlySummary>(`/summary?month=${month}`, token);

// --- Budgets ---
export const getBudgets = (token: string) => apiGet<Budget[]>("/budgets", token);
export const upsertBudgets = (budgets: Budget[], token: string) =>
  apiPut<Budget[]>("/budgets", { budgets }, token);
export const getBudgetSuggestions = (token: string) =>
  apiGet<BudgetSuggestion[]>("/budgets/suggestions", token);
export const deleteBudget = (categoryId: string, token: string) =>
  apiDelete(`/budgets/${categoryId}`, token);

// --- Analysis (AI) ---
export const getInsights = (month: string, token: string) =>
  apiGet<InsightCard[]>(`/insights?month=${month}`, token);
export const askAssistant = (question: string, token: string) =>
  apiPost<AssistantAnswer>("/assistant/query", { question }, token);
