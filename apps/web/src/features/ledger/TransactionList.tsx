import { useAutoAnimate } from "@formkit/auto-animate/react";
import { useState } from "react";
import { CategoryIcon } from "../../lib/categoryIcon";
import { colorForCategory, formatKRW, formatTimeKST } from "../../lib/money";
import type { Category, Transaction } from "../../lib/types";

interface Props {
  transactions: Transaction[];
  categories: Category[];
  onDelete: (tx: Transaction) => void;
  onRecategorize: (id: string, categoryId: string | null) => void;
}

export function TransactionList({ transactions, categories, onDelete, onRecategorize }: Props) {
  const [listRef] = useAutoAnimate<HTMLUListElement>();
  const nameOf = (id: string | null) =>
    categories.find((c) => c.id === id)?.name ?? "미분류";

  return (
    <ul className="tx-list" ref={listRef}>
      {transactions.map((tx) => (
        <TxRow
          key={tx.id}
          tx={tx}
          categories={categories}
          name={nameOf(tx.category_id)}
          onDelete={onDelete}
          onRecategorize={onRecategorize}
        />
      ))}
    </ul>
  );
}

interface RowProps {
  tx: Transaction;
  categories: Category[];
  name: string;
  onDelete: (tx: Transaction) => void;
  onRecategorize: (id: string, categoryId: string | null) => void;
}

function TxRow({ tx, categories, name, onDelete, onRecategorize }: RowProps) {
  const [editing, setEditing] = useState(false);
  const color = colorForCategory(tx.category_id);
  const sign = tx.direction === "income" ? "+" : tx.direction === "expense" ? "-" : "";

  return (
    <li className="tx-item">
      <span
        className="tx-chip"
        style={{ background: `color-mix(in srgb, ${color} 18%, transparent)` }}
      >
        <CategoryIcon name={name} color={color} />
      </span>
      <div className="tx-main">
        <span className="tx-memo">{tx.memo || name}</span>
        {editing ? (
          <select
            className="tx-cat-select"
            value={tx.category_id ?? ""}
            autoFocus
            onChange={(e) => {
              onRecategorize(tx.id, e.target.value || null);
              setEditing(false);
            }}
            onBlur={() => setEditing(false)}
          >
            <option value="">미분류</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        ) : (
          <button
            type="button"
            className="tx-sub tx-sub-edit"
            aria-label={`${name} 카테고리 변경`}
            onClick={() => setEditing(true)}
          >
            {tx.direction === "transfer" ? "이체 · " : ""}
            {name} · {tx.occurred_on.slice(5)}
            <span className="tx-time"> {formatTimeKST(tx.created_at)}</span>
            <span className="tx-edit-hint">✎</span>
          </button>
        )}
      </div>
      <div className="tx-side">
        <span className={`tx-amount ${tx.direction}`}>
          {sign}
          {formatKRW(tx.amount_minor)}
        </span>
        <button
          type="button"
          className="icon-btn"
          aria-label="삭제"
          onClick={() => onDelete(tx)}
        >
          ×
        </button>
      </div>
    </li>
  );
}
