import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { ThreeState } from "../../components/states";
import { archiveCategory, createCategory } from "../../lib/budget";
import { CategoryIcon } from "../../lib/categoryIcon";
import { colorForCategory } from "../../lib/money";
import { useCategories } from "./useCategories";

export function CategoryScreen() {
  const token = useToken();
  const { categories, loading, error, reload } = useCategories();
  const [name, setName] = useState("");
  const [emoji, setEmoji] = useState("");
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed || busy) return;
    setBusy(true);
    setFormError(null);
    try {
      await createCategory(trimmed, emoji.trim() || null, token);
      setName("");
      setEmoji("");
      reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "추가에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    setFormError(null);
    try {
      await archiveCategory(id, token);
      reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "삭제에 실패했습니다.");
    }
  }

  return (
    <div className="category-screen">
      <h2>카테고리</h2>

      <form className="category-form" onSubmit={add}>
        <input
          type="text"
          aria-label="이모지"
          placeholder="🍙"
          maxLength={4}
          className="emoji-input"
          value={emoji}
          onChange={(e) => setEmoji(e.target.value)}
        />
        <input
          type="text"
          aria-label="카테고리 이름"
          placeholder="새 카테고리"
          maxLength={40}
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button type="submit" disabled={busy || !name.trim()}>
          추가
        </button>
      </form>
      {formError && <p className="status status-error" role="alert">{formError}</p>}

      <ThreeState
        loading={loading}
        error={error}
        data={categories}
        emptyMessage="카테고리가 없습니다."
      >
        {(items) => (
          <ul className="category-list">
            {items.map((c) => (
              <li key={c.id} className="category-row">
                <span className="cat-name">
                  <span
                    className="tx-chip"
                    style={{ background: `color-mix(in srgb, ${colorForCategory(c.id)} 18%, transparent)` }}
                  >
                    <CategoryIcon name={c.name} color={colorForCategory(c.id)} />
                  </span>
                  {c.name}
                </span>
                <button
                  type="button"
                  className="icon-btn"
                  aria-label={`${c.name} 보관`}
                  onClick={() => remove(c.id)}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        )}
      </ThreeState>
    </div>
  );
}
