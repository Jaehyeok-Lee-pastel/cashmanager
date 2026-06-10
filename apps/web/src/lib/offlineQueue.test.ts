import { beforeEach, describe, expect, it } from "vitest";
import { clearQueue, enqueue, readQueue } from "./offlineQueue";

describe("offlineQueue", () => {
  beforeEach(() => localStorage.clear());

  it("enqueues, reads in order, and clears", () => {
    expect(readQueue()).toEqual([]);
    expect(enqueue("김밥 4500")).toBe(1);
    expect(enqueue("어제 택시 12000")).toBe(2);
    expect(readQueue()).toEqual(["김밥 4500", "어제 택시 12000"]);
    clearQueue();
    expect(readQueue()).toEqual([]);
  });

  it("returns [] on corrupt storage", () => {
    localStorage.setItem("cm.offlineQueue", "{not json");
    expect(readQueue()).toEqual([]);
  });
});
