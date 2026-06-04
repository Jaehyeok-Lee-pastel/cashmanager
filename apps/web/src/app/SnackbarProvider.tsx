import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react";

interface SnackOptions {
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  duration?: number;
}

const SnackbarContext = createContext<((opts: SnackOptions) => void) | undefined>(undefined);

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [snack, setSnack] = useState<SnackOptions | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const show = useCallback((opts: SnackOptions) => {
    if (timer.current) clearTimeout(timer.current);
    setSnack(opts);
    timer.current = setTimeout(() => setSnack(null), opts.duration ?? 4000);
  }, []);

  const dismiss = useCallback(() => {
    if (timer.current) clearTimeout(timer.current);
    setSnack(null);
  }, []);

  return (
    <SnackbarContext.Provider value={show}>
      {children}
      {snack && (
        <div className="snackbar" role="status">
          <span className="snackbar-msg">{snack.message}</span>
          {snack.actionLabel && (
            <button
              type="button"
              className="snackbar-action"
              onClick={() => {
                snack.onAction?.();
                dismiss();
              }}
            >
              {snack.actionLabel}
            </button>
          )}
        </div>
      )}
    </SnackbarContext.Provider>
  );
}

export function useSnackbar(): (opts: SnackOptions) => void {
  const ctx = useContext(SnackbarContext);
  if (!ctx) throw new Error("useSnackbar must be used within SnackbarProvider");
  return ctx;
}
