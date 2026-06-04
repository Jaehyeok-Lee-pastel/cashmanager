import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { parseLine } from "../../lib/budget";
import type { ParseResult } from "../../lib/types";

interface Props {
  onParsed: (result: ParseResult) => void;
}

export function QuickInputBar({ onParsed }: Props) {
  const token = useToken();
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    setBusy(true);
    setError(null);
    try {
      const result = await parseLine(trimmed, token);
      onParsed(result);
      setText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "분석에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="quick-input" onSubmit={submit}>
      <input
        type="text"
        aria-label="지출 한 줄 입력"
        placeholder="예: 스벅 아메리카노 4900"
        maxLength={200}
        value={text}
        onChange={(e) => setText(e.target.value)}
        autoFocus
      />
      <button type="submit" disabled={busy || !text.trim()}>
        {busy ? "분석…" : "기록"}
      </button>
      {error && <p className="status status-error" role="alert">{error}</p>}
    </form>
  );
}
