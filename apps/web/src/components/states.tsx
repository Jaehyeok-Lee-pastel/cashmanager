import type { ReactNode } from "react";

export function Spinner({ rows = 4 }: { rows?: number }) {
  return (
    <div className="skeleton-list" role="status" aria-label="불러오는 중">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton-row" />
      ))}
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="error-state" role="alert">
      <p className="title">문제가 발생했어요</p>
      <p className="muted">{message}</p>
      {onRetry && (
        <button type="button" className="ghost" onClick={onRetry}>
          다시 시도
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  emoji = "🗒️",
  title,
  message,
  children,
}: {
  emoji?: string;
  title?: string;
  message: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="emoji" aria-hidden>
        {emoji}
      </span>
      {title && <p className="title">{title}</p>}
      <p className="muted">{message}</p>
      {children}
    </div>
  );
}

interface ThreeStateProps<T> {
  loading: boolean;
  error: string | null;
  data: T[] | null;
  emptyMessage: string;
  empty?: ReactNode;
  onRetry?: () => void;
  children: (data: T[]) => ReactNode;
}

/** Renders loading / error / empty / content based on async state. */
export function ThreeState<T>({
  loading,
  error,
  data,
  emptyMessage,
  empty,
  onRetry,
  children,
}: ThreeStateProps<T>) {
  if (loading) return <Spinner />;
  if (error) return <ErrorState message={error} onRetry={onRetry} />;
  if (!data || data.length === 0) {
    return empty ? <>{empty}</> : <EmptyState message={emptyMessage} />;
  }
  return <>{children(data)}</>;
}
