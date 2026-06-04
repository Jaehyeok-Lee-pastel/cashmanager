import { useCallback, useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { listCategories } from "../../lib/budget";
import type { Category } from "../../lib/types";

export function useCategories() {
  const token = useToken();
  const [categories, setCategories] = useState<Category[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    listCategories(token)
      .then(setCategories)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "카테고리 불러오기 실패"),
      )
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(reload, [reload]);

  return { categories, loading, error, reload };
}
