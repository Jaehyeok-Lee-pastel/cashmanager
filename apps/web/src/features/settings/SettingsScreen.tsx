import { useState } from "react";
import { useToken } from "../../app/AuthProvider";
import { exportAllTransactions } from "../../lib/budget";
import { downloadCsv, exportFilename, transactionsToCsv } from "../../lib/exportCsv";
import { AUTO_SAVE_MIN_CONFIDENCE, useAutoSave } from "../../lib/settings";
import { useCategories } from "../categories/useCategories";

export function SettingsScreen() {
  const token = useToken();
  const { categories } = useCategories();
  const [autoSave, setAutoSave] = useAutoSave();
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
    </div>
  );
}
