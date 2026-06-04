import { useEffect, useRef, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { parseLine } from "../../lib/budget";
import type { ParseResult } from "../../lib/types";

interface Props {
  onParsed: (result: ParseResult) => void;
}

// Focus the bar only the first time it mounts this session — otherwise every
// return to the Home tab re-mounts it and pops the mobile keyboard unprompted.
let didAutoFocus = false;

export function QuickInputBar({ onParsed }: Props) {
  const token = useToken();
  const inputRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!didAutoFocus) {
      didAutoFocus = true;
      inputRef.current?.focus();
    }
  }, []);

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
      inputRef.current?.focus(); // keep keyboard up for continuous logging
    } catch (err) {
      setError(err instanceof Error ? err.message : "분석에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="quick-input" onSubmit={submit}>
      <input
        ref={inputRef}
        type="text"
        aria-label="지출 한 줄 입력"
        placeholder="예: 어제 김밥 4500 (말하거나 입력)"
        maxLength={200}
        enterKeyHint="send"
        autoCapitalize="off"
        autoCorrect="off"
        spellCheck={false}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button type="submit" disabled={busy || !text.trim()}>
        {busy ? "분석…" : "기록"}
      </button>
      {error && <p className="status status-error" role="alert">{error}</p>}
    </form>
  );
}
