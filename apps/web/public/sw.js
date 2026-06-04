// Service worker: makes the app installable + caches the app shell ONLY.
// API responses (personal financial data) are NEVER cached — even though the
// single-service deploy serves them on the same origin.
const CACHE = "cashmanager-v2";

// same-origin API paths that must bypass the cache (network-only)
const API_PREFIXES = [
  "/me", "/categories", "/transactions", "/summary",
  "/budgets", "/insights", "/assistant", "/health",
];

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) =>
  event.waitUntil(
    (async () => {
      // drop old caches (e.g. v1, which may hold financial API responses)
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
      await self.clients.claim();
    })(),
  ),
);

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (API_PREFIXES.some((p) => url.pathname.startsWith(p))) return; // never cache API

  // stale-while-revalidate for the app shell (HTML/JS/CSS/icons)
  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const cached = await cache.match(req);
      const network = fetch(req)
        .then((res) => {
          if (res.ok) cache.put(req, res.clone());
          return res;
        })
        .catch(() => cached);
      return cached || network;
    }),
  );
});
