import { describe, expect, it } from "vitest";
import {
  colorForCategory,
  currentMonth,
  formatKRW,
  formatTimeKST,
  shiftMonth,
  todayKST,
} from "./money";

describe("money", () => {
  it("formats KRW with commas", () => {
    expect(formatKRW(4900)).toBe("4,900원");
    expect(formatKRW(1234567)).toBe("1,234,567원");
    expect(formatKRW(0)).toBe("0원");
  });

  it("shifts month across year boundaries", () => {
    expect(shiftMonth("2026-06", -1)).toBe("2026-05");
    expect(shiftMonth("2026-12", 1)).toBe("2027-01");
    expect(shiftMonth("2026-01", -1)).toBe("2025-12");
  });

  it("maps category to a stable palette token", () => {
    expect(colorForCategory(null)).toBe("var(--color-text-3)");
    const a = colorForCategory("cat-1");
    expect(colorForCategory("cat-1")).toBe(a);
    expect(a).toMatch(/^var\(--cat-[1-8]\)$/);
  });

  it("produces well-formed KST month/day strings", () => {
    expect(currentMonth()).toMatch(/^\d{4}-\d{2}$/);
    expect(todayKST()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it("formats a UTC timestamp as KST wall-clock time", () => {
    // 05:14 UTC + 9h = 14:14 KST
    expect(formatTimeKST("2026-06-11T05:14:00Z")).toMatch(/14.?14/);
    // crossing midnight: 16:30 UTC = 01:30 KST next day
    expect(formatTimeKST("2026-06-11T16:30:00Z")).toMatch(/01.?30/);
    expect(formatTimeKST("not-a-date")).toBe("");
  });
});
