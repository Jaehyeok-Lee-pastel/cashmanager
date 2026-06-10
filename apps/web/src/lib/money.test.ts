import { describe, expect, it } from "vitest";
import { colorForCategory, currentMonth, formatKRW, shiftMonth, todayKST } from "./money";

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
});
