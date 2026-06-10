import { useState } from "react";

const AUTO_SAVE_KEY = "cm.autoSave";
const THEME_KEY = "cm.theme";
const TEXT_KEY = "cm.textSize";

export type Theme = "dark" | "light";
export type TextSize = "normal" | "large";

/** Apply theme/text-size to <html> via data-attributes (CSS token overrides). */
export function applyTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme;
}
export function applyTextSize(size: TextSize) {
  document.documentElement.dataset.text = size;
}

/** Read+apply persisted appearance once at startup (called from main.tsx). */
export function initAppearance() {
  applyTheme((localStorage.getItem(THEME_KEY) as Theme) || "dark");
  applyTextSize((localStorage.getItem(TEXT_KEY) as TextSize) || "normal");
}

export function useTheme(): [Theme, (v: Theme) => void] {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(THEME_KEY) as Theme) || "dark",
  );
  const set = (v: Theme) => {
    localStorage.setItem(THEME_KEY, v);
    applyTheme(v);
    setTheme(v);
  };
  return [theme, set];
}

export function useTextSize(): [TextSize, (v: TextSize) => void] {
  const [size, setSize] = useState<TextSize>(
    () => (localStorage.getItem(TEXT_KEY) as TextSize) || "normal",
  );
  const set = (v: TextSize) => {
    localStorage.setItem(TEXT_KEY, v);
    applyTextSize(v);
    setSize(v);
  };
  return [size, set];
}

/** Auto-save kicks in only for very confident parses. */
export const AUTO_SAVE_MIN_CONFIDENCE = 0.95;

/** localStorage-backed per-device preference (default OFF — conservative). */
export function useAutoSave(): [boolean, (value: boolean) => void] {
  const [on, setOn] = useState<boolean>(
    () => localStorage.getItem(AUTO_SAVE_KEY) === "1",
  );
  const set = (value: boolean) => {
    localStorage.setItem(AUTO_SAVE_KEY, value ? "1" : "0");
    setOn(value);
  };
  return [on, set];
}
