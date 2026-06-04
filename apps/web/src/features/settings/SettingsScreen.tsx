import { AUTO_SAVE_MIN_CONFIDENCE, useAutoSave } from "../../lib/settings";

export function SettingsScreen() {
  const [autoSave, setAutoSave] = useAutoSave();
  const pct = Math.round(AUTO_SAVE_MIN_CONFIDENCE * 100);

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
    </div>
  );
}
