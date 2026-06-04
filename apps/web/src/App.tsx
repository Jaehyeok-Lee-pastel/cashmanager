import { useState } from "react";
import { useAuth } from "./app/AuthProvider";
import { Spinner } from "./components/states";
import { LoginScreen } from "./features/auth/LoginScreen";
import { AnalysisScreen } from "./features/analysis/AnalysisScreen";
import { BudgetScreen } from "./features/budgets/BudgetScreen";
import { CategoryScreen } from "./features/categories/CategoryScreen";
import { HomeScreen } from "./features/ledger/HomeScreen";
import { SummaryScreen } from "./features/summary/SummaryScreen";
import { currentMonth } from "./lib/money";

type View = "home" | "summary" | "analysis" | "budgets" | "categories";

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
        {view === "summary" && <SummaryScreen month={month} onMonthChange={setMonth} />}
        {view === "analysis" && <AnalysisScreen month={month} />}
        {view === "budgets" && <BudgetScreen />}
        {view === "categories" && <CategoryScreen />}
      </main>

      <nav className="bottom-nav" aria-label="주요 메뉴">
        <button type="button" className={view === "home" ? "active" : ""} onClick={() => setView("home")}>
          기록
        </button>
        <button type="button" className={view === "summary" ? "active" : ""} onClick={() => setView("summary")}>
          요약
        </button>
        <button type="button" className={view === "analysis" ? "active" : ""} onClick={() => setView("analysis")}>
          분석
        </button>
        <button type="button" className={view === "budgets" ? "active" : ""} onClick={() => setView("budgets")}>
          예산
        </button>
        <button type="button" className={view === "categories" ? "active" : ""} onClick={() => setView("categories")}>
          카테고리
        </button>
      </nav>
    </div>
  );
}
