import { useCallback, useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { listTransactions } from "../../lib/budget";
import type { Transaction } from "../../lib/types";

interface State {
  transactions: Transaction[] | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
  prepend: (tx: Transaction) => void;
  remove: (id: string) => void;
}

export function useTransactions(month: string): State {
  const token = useToken();
  const [transactions, setTransactions] = useState<Transaction[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    listTransactions(month, token)
      .then(setTransactions)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "불러오기 실패"),
      )
      .finally(() => setLoading(false));
  }, [month, token]);

  useEffect(reload, [reload]);

  const prepend = useCallback(
    (tx: Transaction) => setTransactions((prev) => [tx, ...(prev ?? [])]),
    [],
  );
  const remove = useCallback(
    (id: string) =>
      setTransactions((prev) => (prev ?? []).filter((t) => t.id !== id)),
    [],
  );

  return { transactions, loading, error, reload, prepend, remove };
}
