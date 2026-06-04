import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { EmptyState, ThreeState } from "../../components/states";
import { parseLine } from "../../lib/budget";
import { formatKRW } from "../../lib/money";
import type { ParseResult, Transaction } from "../../lib/types";
import { useCategories } from "../categories/useCategories";
import { ParseConfirmCard } from "./ParseConfirmCard";
import { QuickInputBar } from "./QuickInputBar";
import { TransactionList } from "./TransactionList";
import { useTransactions } from "./useTransactions";

const EXAMPLES = ["스벅 아메리카노 4900", "어제 택시 12000", "점심 김밥 8천원"];

export function HomeScreen({ month }: { month: string }) {
  const token = useToken();
  const { categories } = useCategories();
  const { transactions, loading, error, reload, prepend, remove } =
    useTransactions(month);
  const [pending, setPending] = useState<ParseResult | null>(null);

  const monthExpense = (transactions ?? [])
    .filter((t) => t.direction === "expense")
    .reduce((sum, t) => sum + t.amount_minor, 0);

  function onSaved(tx: Transaction) {
    prepend(tx);
    setPending(null);
  }

  async function runExample(text: string) {
    try {
      setPending(await parseLine(text, token));
    } catch {
      // ignore; user can type manually
    }
  }

  return (
    <div className="home">
      <header className="month-header">
        <span className="label">{month} 지출</span>
        <strong className="tabular">{formatKRW(monthExpense)}</strong>
      </header>

      <QuickInputBar onParsed={setPending} />

      {pending && (
        <ParseConfirmCard
          result={pending}
          categories={categories ?? []}
          onSaved={onSaved}
          onCancel={() => setPending(null)}
        />
      )}

      <ThreeState
        loading={loading}
        error={error}
        data={transactions}
        emptyMessage=""
        onRetry={reload}
        empty={
          <EmptyState
            emoji="✍️"
            title="아직 기록이 없어요"
            message="위에 한 줄 적거나, 아래 예시를 눌러보세요."
          >
            <div className="empty-chips">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  type="button"
                  className="chip"
                  onClick={() => runExample(ex)}
                >
                  {ex}
                </button>
              ))}
            </div>
          </EmptyState>
        }
      >
        {(txs) => (
          <TransactionList
            transactions={txs}
            categories={categories ?? []}
            onDeleted={remove}
          />
        )}
      </ThreeState>
    </div>
  );
}
