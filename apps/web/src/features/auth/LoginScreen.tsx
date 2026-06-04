import { useState } from "react";
import { supabase } from "../../lib/supabase";

type Mode = "signin" | "signup";

export function LoginScreen() {
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setNotice(null);
    setBusy(true);
    try {
      if (mode === "signin") {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setNotice("가입 확인 메일을 보냈어요. 메일을 확인해주세요.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  async function google() {
    setError(null);
    const { error } = await supabase.auth.signInWithOAuth({ provider: "google" });
    if (error) setError(error.message);
  }

  async function resetPassword() {
    setError(null);
    setNotice(null);
    if (!email.trim()) {
      setError("이메일을 먼저 입력해주세요.");
      return;
    }
    // Always show the same message whether or not the account exists, so this
    // can't be used to probe which emails are registered (no enumeration).
    const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
      redirectTo: window.location.origin,
    });
    if (error) console.warn("resetPasswordForEmail:", error.message);
    setNotice("입력하신 이메일이 가입되어 있다면 재설정 링크를 보냈어요. 메일함을 확인해주세요.");
  }

  return (
    <main className="app-shell auth">
      <h1>캐시매니저</h1>
      <p className="muted">한 줄이면 기록 끝.</p>

      <form className="card" onSubmit={submit}>
        <h2>{mode === "signin" ? "로그인" : "회원가입"}</h2>

        <label htmlFor="email">이메일</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label htmlFor="password">비밀번호</label>
        <input
          id="password"
          type="password"
          autoComplete={mode === "signin" ? "current-password" : "new-password"}
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="status status-error" role="alert">{error}</p>}
        {notice && <p className="status status-ok" role="status">{notice}</p>}

        <button type="submit" disabled={busy}>
          {busy ? "처리 중…" : mode === "signin" ? "로그인" : "가입하기"}
        </button>
        <button type="button" className="ghost" onClick={google}>
          Google로 계속하기
        </button>

        <button
          type="button"
          className="link"
          onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
        >
          {mode === "signin" ? "계정이 없으신가요? 회원가입" : "이미 계정이 있으신가요? 로그인"}
        </button>

        {mode === "signin" && (
          <button type="button" className="link" onClick={resetPassword}>
            비밀번호를 잊으셨나요?
          </button>
        )}
      </form>
    </main>
  );
}
