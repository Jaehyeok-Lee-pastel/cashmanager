import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { exportAllTransactions } from "../../lib/budget";
import { downloadCsv, exportFilename, transactionsToCsv } from "../../lib/exportCsv";
import {
  AUTO_SAVE_MIN_CONFIDENCE,
  useAutoSave,
  useTextSize,
  useTheme,
} from "../../lib/settings";
import { useCategories } from "../categories/useCategories";

export function SettingsScreen() {
  const token = useToken();
  const { categories } = useCategories();
  const [autoSave, setAutoSave] = useAutoSave();
  const [theme, setTheme] = useTheme();
  const [textSize, setTextSize] = useTextSize();
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const pct = Math.round(AUTO_SAVE_MIN_CONFIDENCE * 100);

  async function exportCsv() {
    setExporting(true);
    setExportMsg(null);
    try {
      const transactions = await exportAllTransactions(token);
      if (transactions.length === 0) {
        setExportMsg("내보낼 거래가 아직 없어요.");
        return;
      }
      downloadCsv(transactionsToCsv(transactions, categories ?? []), exportFilename());
      setExportMsg(`${transactions.length}건을 내보냈어요.`);
    } catch (err) {
      setExportMsg(err instanceof Error ? err.message : "내보내기에 실패했어요.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="settings-screen">
      <h2>설정</h2>

      <div className="setting-row">
        <span className="setting-text">
          <span className="setting-title">화면 테마</span>
          <span className="setting-desc">밝은 곳에서는 라이트가 더 잘 보여요.</span>
        </span>
        <div className="segmented" role="group" aria-label="화면 테마">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              type="button"
              className={theme === t ? "active" : ""}
              aria-pressed={theme === t}
              onClick={() => setTheme(t)}
            >
              {t === "dark" ? "다크" : "라이트"}
            </button>
          ))}
        </div>
      </div>

      <div className="setting-row">
        <span className="setting-text">
          <span className="setting-title">글씨 크기</span>
          <span className="setting-desc">작게 느껴지면 크게로 바꿔보세요.</span>
        </span>
        <div className="segmented" role="group" aria-label="글씨 크기">
          {(["normal", "large"] as const).map((s) => (
            <button
              key={s}
              type="button"
              className={textSize === s ? "active" : ""}
              aria-pressed={textSize === s}
              onClick={() => setTextSize(s)}
            >
              {s === "normal" ? "보통" : "크게"}
            </button>
          ))}
        </div>
      </div>

      <label className="setting-row">
        <span className="setting-text">
          <span className="setting-title">고신뢰 자동저장</span>
          <span className="setting-desc">
            AI 분석이 아주 확실할 때(신뢰도 {pct}% 이상) 확인 단계를 건너뛰고 바로
            저장해요. 저장 직후 “실행취소”로 되돌릴 수 있어요. (애매하면 기존처럼
            확인 카드가 떠요)
          </span>
        </span>
        <input
          type="checkbox"
          className="switch"
          role="switch"
          aria-label="고신뢰 자동저장"
          checked={autoSave}
          onChange={(e) => setAutoSave(e.target.checked)}
        />
      </label>

      <div className="setting-row">
        <span className="setting-text">
          <span className="setting-title">데이터 내보내기</span>
          <span className="setting-desc">
            전체 거래 내역을 CSV 파일로 저장해요. 엑셀·구글시트로 열 수 있고,
            가계부를 직접 백업해 두는 용도로 써요.
          </span>
        </span>
        <button type="button" className="ghost" onClick={exportCsv} disabled={exporting}>
          {exporting ? "준비 중…" : "CSV로 내보내기"}
        </button>
      </div>
      {exportMsg && <p className="status" role="status">{exportMsg}</p>}

      <h3 className="section-label">카드 사용 팁</h3>
      <p className="muted card-tip">
        카드로 쓸 때마다 한 줄씩 적으면 지출로 기록돼요. <strong>월 카드대금은 안 적어도 돼요</strong>
        (이미 개별 결제로 다 잡혔어요). 통장 흐름까지 맞추고 싶어 “카드대금 120만”처럼 적으면
        <strong>‘이체’</strong>로 저장돼 지출 합계엔 들어가지 않아요.
      </p>
    </div>
  );
}
