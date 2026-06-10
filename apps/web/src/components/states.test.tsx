import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyState, ErrorState, ThreeState } from "./states";

describe("states", () => {
  it("EmptyState shows title + message + child", () => {
    render(
      <EmptyState title="아직 기록이 없어요" message="한 줄 적어보세요">
        <button>예시</button>
      </EmptyState>,
    );
    expect(screen.getByText("아직 기록이 없어요")).toBeTruthy();
    expect(screen.getByText("한 줄 적어보세요")).toBeTruthy();
    expect(screen.getByRole("button", { name: "예시" })).toBeTruthy();
  });

  it("ErrorState renders an alert with a retry action", () => {
    const onRetry = vi.fn();
    render(<ErrorState message="불러오기 실패" onRetry={onRetry} />);
    expect(screen.getByRole("alert").textContent).toContain("불러오기 실패");
  });

  it("ThreeState renders the empty branch when data is an empty list", () => {
    render(
      <ThreeState loading={false} error={null} data={[]} emptyMessage="비어 있어요">
        {() => <div>list</div>}
      </ThreeState>,
    );
    expect(screen.getByText("비어 있어요")).toBeTruthy();
    expect(screen.queryByText("list")).toBeNull();
  });
});
