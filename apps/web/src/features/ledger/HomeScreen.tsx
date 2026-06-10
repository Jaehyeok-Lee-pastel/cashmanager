import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { useSnackbar } from "../../app/SnackbarProvider";
import { EmptyState, ThreeState } from "../../components/states";
import {
  createTransaction,
  deleteTransaction,
  parseLine,
  parseResultToCreate,
  updateTransaction,
} from "../../lib/budget";
import { formatKRW } from "../../lib/money";
import { recentChips } from "../../lib/recent";
import { AUTO_SAVE_MIN_CONFIDENCE, useAutoSave } from "../../lib/settings";
import type { ParseResult, Transaction } from "../../lib/types";
import { useCategories } from "../categories/useCategories";
import { ParseConfirmCard } from "./ParseConfirmCard";
import { QuickInputBar } from "./QuickInputBar";
import { TransactionList } from "./TransactionList";
import { useTransactions } from "./useTransactions";

const EXAMPLES = ["스벅 아메리카노 4900", "어제 택시 12000", "점심 김밥 8천원"];

export function HomeScreen({ month }: { month: string }) {
  const token = useToken();
  const showSnackbar = useSnackbar();
  const [autoSave, setAutoSave] = useAutoSave();
  const { categories } = useCategories();
  const { transactions, loading, error, reload, prepend, remove } =
    useTransactions(month);
  const [pending, setPending] = useState<ParseResult | null>(null);
  const [showTip, setShowTip] = useState(
    () => localStorage.getItem("cm.onboardSeen") !== "1",
  );
  const dismissTip = () => {
    localStorage.setItem("cm.onboardSeen", "1");
    setShowTip(false);
  };
  const enableAutoSave = () => {
    setAutoSave(true);
    dismissTip();
    showSnackbar({ message: "자동저장을 켰어요 — 확실한 건 확인 없이 저장돼요" });
  };

  const monthExpense = (transactions ?? [])
    .filter((t) => t.direction === "expense")
    .reduce((sum, t) => sum + t.amount_minor, 0);
  const chips = recentChips(transactions ?? []);

  function onSaved(tx: Transaction) {
    prepend(tx);
    setPending(null);
  }

  // auto-save when very confident (and the user enabled it); else show confirm card
  async function handleParsed(result: ParseResult) {
    const eligible =
      autoSave &&
      !result.needs_manual &&
      result.confidence >= AUTO_SAVE_MIN_CONFIDENCE &&
      !!result.amount_minor &&
      !!result.category_id;
    if (!eligible) {
      setPending(result);
      return;
    }
    try {
      const tx = await createTransaction(parseResultToCreate(result), token);
      prepend(tx);
      showSnackbar({
        message: `저장됨 · ${formatKRW(tx.amount_minor)}`,
        actionLabel: "실행취소",
        onAction: () => {
          remove(tx.id);
          deleteTransaction(tx.id, token).catch(() => {});
        },
      });
    } catch {
      setPending(result); // never silently drop — fall back to manual confirm
    }
  }

  async function quickEntry(text: string) {
    try {
      handleParsed(await parseLine(text, token));
    } catch {
      // parse failed (token expired / network) — tell the user instead of
      // letting the chip feel dead.
      showSnackbar({ message: "분석에 실패했어요. 직접 입력해주세요." });
    }
  }

  // correcting a category also re-trains the merchant map (server-side), so the
  // next auto-classify of that merchant is right.
  async function onRecategorize(id: string, categoryId: string | null) {
    try {
      await updateTransaction(id, { category_id: categoryId }, token);
      reload();
      showSnackbar({ message: "카테고리를 바꿨어요" });
    } catch {
      showSnackbar({ message: "변경에 실패했어요" });
    }
  }

  // optimistic delete + undo snackbar; real delete fires after the snackbar window
  function onDelete(tx: Transaction) {
    remove(tx.id);
    let undone = false;
    const timer = setTimeout(() => {
      if (!undone) deleteTransaction(tx.id, token).catch(() => {});
    }, 4000);
    showSnackbar({
      message: "삭제됨",
      actionLabel: "실행취소",
      duration: 4000,
      onAction: () => {
        undone = true;
        clearTimeout(timer);
        reload();
      },
    });
  }

  return (
    <div className="home">
      {showTip && (
        <div className="onboard-banner" role="note">
          <button
            type="button"
            className="onboard-close"
            aria-label="안내 닫기"
            onClick={dismissTip}
          >
            ×
          </button>
          <strong>한 줄로 적어보세요</strong>
          <p>
            "스벅 4900" · "어제 택시 12000" 처럼 적으면 AI가 금액·카테고리·날짜를 잡아줘요.
          </p>
          {!autoSave && (
            <div className="onboard-cta-row">
              <button type="button" className="onboard-cta" onClick={enableAutoSave}>
                고신뢰 자동저장 켜기
              </button>
              <span className="onboard-cta-note">
                확실한 건 확인 없이 바로 저장돼요 (실행취소 가능)
              </span>
            </div>
          )}
        </div>
      )}
      <header className="month-header">
        <span className="label">{month} 지출</span>
        <strong className="tabular">{formatKRW(monthExpense)}</strong>
      </header>

      <ThreeState
        loading={loading}
        error={error}
        data={transactions}
        emptyMessage=""
        onRetry={reload}
        empty={
          <EmptyState
            emoji="✍️"
            title="아직 기록이 없어요"
            message="아래에 한 줄 적거나, 예시를 눌러보세요."
          >
            <div className="empty-chips">
              {EXAMPLES.map((ex) => (
                <button key={ex} type="button" className="chip" onClick={() => quickEntry(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </EmptyState>
        }
      >
        {(txs) => (
          <TransactionList
            transactions={txs}
            categories={categories ?? []}
            onDelete={onDelete}
            onRecategorize={onRecategorize}
          />
        )}
      </ThreeState>

      <div className="input-dock">
        {pending && (
          <ParseConfirmCard
            result={pending}
            categories={categories ?? []}
            onSaved={onSaved}
            onCancel={() => setPending(null)}
          />
        )}
        {!pending && chips.length > 0 && (
          <div className="recent-chips">
            {chips.map((c) => (
              <button key={c.raw} type="button" className="chip" onClick={() => quickEntry(c.raw)}>
                {c.label}
              </button>
            ))}
          </div>
        )}
        <QuickInputBar onParsed={handleParsed} />
      </div>
    </div>
  );
}
