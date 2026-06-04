# web (React + Vite + TypeScript)

## Run (Windows / PowerShell)

```powershell
cd apps/web
npm install
Copy-Item .env.example .env.local   # then fill in API base + Supabase anon key
npm run dev
```

Dev server: http://localhost:5173 (proxies API calls to `VITE_API_BASE_URL`).
Build: `npm run build` · Typecheck: `npm run typecheck`

## Layout

```
src/
  main.tsx        entry
  App.tsx         root component (pings /health to verify API wiring)
  lib/api.ts      fetch wrapper (apiGet/apiPost) — all API calls go through here
  lib/supabase.ts the only frontend Supabase client (anon key only)
  components/      shared/layout UI
  pages/          (or features/{domain}/ as the app grows)
  styles.css
```

Rules: see [`docs/08_coding_guidelines/03_react_typescript.md`](../../docs/08_coding_guidelines/03_react_typescript.md).
