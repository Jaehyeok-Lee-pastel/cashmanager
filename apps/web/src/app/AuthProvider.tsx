import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "../lib/supabase";

interface AuthState {
  session: Session | null;
  token: string | null;
  loading: boolean;
  recovery: boolean; // arrived via a password-reset email link
  clearRecovery: () => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

// Persisted across reloads: a recovery session stays logged in, so the reset
// gate must survive a page refresh — otherwise reloading would let the
// recovery session into the normal app without choosing a new password.
const RECOVERY_KEY = "cm_pw_recovery";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [recovery, setRecovery] = useState(
    () => sessionStorage.getItem(RECOVERY_KEY) === "1",
  );

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((event, next) => {
      // password-reset link opens the app with a recovery session: show the
      // "set new password" screen instead of the normal app.
      if (event === "PASSWORD_RECOVERY") {
        sessionStorage.setItem(RECOVERY_KEY, "1");
        setRecovery(true);
      }
      setSession(next);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  const endRecovery = () => {
    sessionStorage.removeItem(RECOVERY_KEY);
    setRecovery(false);
  };

  const value: AuthState = {
    session,
    token: session?.access_token ?? null,
    loading,
    recovery,
    clearRecovery: endRecovery,
    signOut: async () => {
      endRecovery();
      await supabase.auth.signOut();
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

/** Token guaranteed non-null inside authenticated screens. */
export function useToken(): string {
  const { token } = useAuth();
  if (!token) {
    throw new Error("useToken used outside an authenticated screen");
  }
  return token;
}
