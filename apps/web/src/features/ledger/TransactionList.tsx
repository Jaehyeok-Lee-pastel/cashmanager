import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useToken } from "../../app/AuthProvider";
import { CategoryIcon } from "../../lib/categoryIcon";
import { deleteTransaction } from "../../lib/budget";
import { colorForCategory, formatKRW } from "../../lib/money";
import type { Category, Transaction } from "../../lib/types";

interface Props {
  transactions: Transaction[];
  categories: Category[];
  onDeleted: (id: string) => void;
}

export function TransactionList({ transactions, categories, onDeleted }: Props) {
  const token = useToken();
  const [listRef] = useAutoAnimate<HTMLUListElement>();
  const catOf = (id: string | null) => categories.find((c) => c.id === id);
  const nameOf = (id: string | null) => catOf(id)?.name ?? "미분류";

  async function remove(id: string) {
    onDeleted(id); // optimistic
    try {
      await deleteTransaction(id, token);
    } catch {
      // best-effort: a later reload reconciles if this failed
    }
  }

  return (
    <ul className="tx-list" ref={listRef}>
      {transactions.map((tx) => {
        const color = colorForCategory(tx.category_id);
        return (
          <li key={tx.id} className="tx-item">
            <span
              className="tx-chip"
              style={{ background: `color-mix(in srgb, ${color} 18%, transparent)` }}
            >
              <CategoryIcon name={nameOf(tx.category_id)} color={color} />
            </span>
            <div className="tx-main">
              <span className="tx-memo">{tx.memo || nameOf(tx.category_id)}</span>
              <span className="tx-sub">
                {nameOf(tx.category_id)} · {tx.occurred_on.slice(5)}
              </span>
            </div>
            <div className="tx-side">
              <span className={`tx-amount ${tx.direction}`}>
                {tx.direction === "income" ? "+" : "-"}
                {formatKRW(tx.amount_minor)}
              </span>
              <button
                type="button"
                className="icon-btn"
                aria-label="삭제"
                onClick={() => remove(tx.id)}
              >
                ×
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
