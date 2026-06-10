// Offline write queue: when there's no network, a typed line is stashed locally
// (raw text) and replayed when connectivity returns — so "지하철에서 김밥 4500"
// isn't lost. localStorage is enough; the queue is tiny and personal.
const KEY = "cm.offlineQueue";

export function readQueue(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(v) ? v : [];
  } catch {
    return [];
  }
}

export function enqueue(text: string): number {
  const q = readQueue();
  q.push(text);
  localStorage.setItem(KEY, JSON.stringify(q));
  return q.length;
}

export function clearQueue(): void {
  localStorage.removeItem(KEY);
}
