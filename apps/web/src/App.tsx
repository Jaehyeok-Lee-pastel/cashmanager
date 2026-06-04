import { useState } from "react";
import { useAuth } from "./app/AuthProvider";
import { Spinner } from "./components/states";
import { LoginScreen } from "./features/auth/LoginScreen";
import { AnalysisScreen } from "./features/analysis/AnalysisScreen";
import { BudgetScreen } from "./features/budgets/BudgetScreen";
import { CategoryScreen } from "./features/categories/CategoryScreen";
import { HistoryScreen } from "./features/history/HistoryScreen";
import { HomeScreen } from "./features/ledger/HomeScreen";
import { MoreScreen } from "./features/more/MoreScreen";
import { SettingsScreen } from "./features/settings/SettingsScreen";
import { SummaryScreen } from "./features/summary/SummaryScreen";
import { currentMonth } from "./lib/money";

type View =
  | "home"
  | "history"
  | "summary"
  | "analysis"
  | "more"
  | "budgets"
  | "categories"
  | "settings";

const TABS: { key: View; label: string }[] = [
  { key: "home", label: "기록" },
  { key: "history", label: "내역" },
  { key: "summary", label: "요약" },
  { key: "analysis", label: "분석" },
  { key: "more", label: "더보기" },
];

// which top-level tab stays highlighted while in a "더보기" sub-screen
const MORE_SUBVIEWS: View[] = ["more", "budgets", "categories", "settings"];

export function App() {
  const { session, loading, signOut } = useAuth();
  const [view, setView] = useState<View>("home");
  const [month, setMonth] = useState<string>(currentMonth());

  if (loading) {
    return (
      <main className="app-shell">
        <Spinner />
      </main>
    );
  }

  if (!session) {
    return <LoginScreen />;
  }

  const activeTab = MORE_SUBVIEWS.includes(view) ? "more" : view;

  return (
    <div className="app-shell">
      <header className="top-bar">
        <h1>캐시매니저</h1>
        <button type="button" className="link" onClick={signOut}>
          로그아웃
        </button>
      </header>

      <main className="content">
        {view === "home" && <HomeScreen month={month} />}
        {view === "history" && <HistoryScreen month={month} onMonthChange={setMonth} />}
        {view === "summary" && <SummaryScreen month={month} onMonthChange={setMonth} />}
        {view === "analysis" && <AnalysisScreen month={month} />}
        {view === "more" && <MoreScreen onNavigate={setView} />}
        {view === "budgets" && <BudgetScreen />}
        {view === "categories" && <CategoryScreen />}
        {view === "settings" && <SettingsScreen />}
      </main>

      <nav className="bottom-nav" aria-label="주요 메뉴">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            className={activeTab === tab.key ? "active" : ""}
            aria-current={activeTab === tab.key ? "page" : undefined}
            onClick={() => setView(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}
