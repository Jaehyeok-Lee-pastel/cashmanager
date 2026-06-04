# api (FastAPI)

## Run (Windows / PowerShell)

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in Supabase keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: http://localhost:8000/health · Docs: http://localhost:8000/docs

## Layout

```
app/
  main.py            FastAPI app factory (create_app), CORS, router includes
  core/config.py     pydantic-settings (.env)
  api/deps.py        get_current_user (Supabase JWT) → CurrentUser / CurrentUserDep
  api/routes/        thin HTTP routers (health.py included; add domain routers here)
  services/          business logic; supabase.py = the only backend Supabase client
  repositories/      DB access helpers (optional split from services)
  schemas/           Pydantic request/response models
  tests/             pytest (test_health.py)
```

Rules: see [`docs/08_coding_guidelines/02_python_fastapi.md`](../../docs/08_coding_guidelines/02_python_fastapi.md).
