import { useState } from "react";

const AUTO_SAVE_KEY = "cm.autoSave";

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
