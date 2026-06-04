import { useState } from "react";
import { useAuth } from "../../app/AuthProvider";
import { supabase } from "../../lib/supabase";

const MIN_PASSWORD = 6;

/** Shown after the user opens a password-reset email link (recovery session). */
export function ResetPasswordScreen() {
  const { clearRecovery, signOut } = useAuth();
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < MIN_PASSWORD) {
      setError(`비밀번호는 ${MIN_PASSWORD}자 이상이어야 해요.`);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const { error: updateError } = await supabase.auth.updateUser({ password });
      if (updateError) throw updateError;
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "변경에 실패했어요.");
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <main className="app-shell auth">
        <h1>캐시매니저</h1>
        <div className="card">
          <h2>완료</h2>
          <p className="status status-ok" role="status">
            비밀번호를 변경했어요. 새 비밀번호로 이용하세요.
          </p>
          <button type="button" onClick={clearRecovery}>
            계속하기
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="app-shell auth">
      <h1>캐시매니저</h1>
      <p className="muted">새 비밀번호를 정해주세요.</p>

      <form className="card" onSubmit={submit}>
        <h2>비밀번호 재설정</h2>

        <label htmlFor="new-password">새 비밀번호</label>
        <input
          id="new-password"
          type="password"
          autoComplete="new-password"
          required
          minLength={MIN_PASSWORD}
          placeholder={`${MIN_PASSWORD}자 이상`}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="status status-error" role="alert">{error}</p>}

        <button type="submit" disabled={busy}>
          {busy ? "변경 중…" : "비밀번호 변경"}
        </button>
        <button
          type="button"
          className="link"
          onClick={async () => {
            await signOut();
          }}
        >
          취소하고 로그인으로
        </button>
      </form>
    </main>
  );
}
