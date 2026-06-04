import { useCallback, useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { getBudgets } from "../../lib/budget";
import type { Budget } from "../../lib/types";

export function useBudgets() {
  const token = useToken();
  const [budgets, setBudgets] = useState<Budget[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    getBudgets(token)
      .then(setBudgets)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "예산 불러오기 실패"),
      )
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(reload, [reload]);

  return { budgets, loading, error, reload };
}
