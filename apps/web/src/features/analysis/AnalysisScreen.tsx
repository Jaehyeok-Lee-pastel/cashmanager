import { useEffect, useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { ErrorState, Spinner } from "../../components/states";
import { askAssistant, getInsights } from "../../lib/budget";
import type { InsightCard } from "../../lib/types";

const EXAMPLES = ["이번 달 카페에 얼마 썼어?", "지난달보다 많이 썼어?", "제일 많이 쓴 카테고리는?"];

export function AnalysisScreen({ month }: { month: string }) {
  const token = useToken();
  const [insights, setInsights] = useState<InsightCard[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [asking, setAsking] = useState(false);

  function loadInsights() {
    setLoading(true);
    setError(null);
    getInsights(month, token)
      .then(setInsights)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "불러오기 실패"))
      .finally(() => setLoading(false));
  }

  useEffect(loadInsights, [month, token]);

  async function ask(q: string) {
    const trimmed = q.trim();
    if (!trimmed || asking) return;
    setAsking(true);
    setAnswer(null);
    try {
      const res = await askAssistant(trimmed, token);
      setAnswer(res.answer);
    } catch {
      setAnswer("답변을 가져오지 못했어요.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="analysis-screen">
      <h2>AI 분석</h2>

      <form
        className="quick-input"
        onSubmit={(e) => {
          e.preventDefault();
          ask(question);
        }}
      >
        <input
          type="text"
          aria-label="가계부에게 질문"
          placeholder="예: 이번 달 카페에 얼마 썼어?"
          maxLength={200}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={asking || !question.trim()}>
          {asking ? "생각 중…" : "물어보기"}
        </button>
      </form>

      <div className="example-chips">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            className="chip"
            onClick={() => {
              setQuestion(ex);
              ask(ex);
            }}
          >
            {ex}
          </button>
        ))}
      </div>

      {(asking || answer) && (
        <div className="answer-card">{asking ? "생각 중…" : answer}</div>
      )}

      <h3 className="section-label">이번 달 인사이트</h3>
      {loading && <Spinner rows={3} />}
      {error && <ErrorState message={error} onRetry={loadInsights} />}
      {insights && !loading && !error && (
        insights.length === 0 ? (
          <p className="status muted">표시할 인사이트가 아직 없어요. 기록이 쌓이면 보여드릴게요.</p>
        ) : (
          <ul className="insight-list">
            {insights.map((c, i) => (
              <li key={i} className={`insight-card sev-${c.severity}`}>
                <span className="insight-title">{c.title}</span>
                <span className="insight-detail">{c.detail}</span>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  );
}
