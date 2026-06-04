import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from app.api.routes import (
    assistant,
    budgets,
    categories,
    health,
    insights,
    me,
    summary,
    transactions,
)
from app.core.config import settings


_API_PREFIXES = ("/me", "/categories", "/transactions", "/summary",
                 "/budgets", "/insights", "/assistant")


def create_app() -> FastAPI:
    is_prod = settings.app_env == "production"
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if is_prod:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # never let caches / service workers store personal financial responses
        if any(request.url.path.startswith(p) for p in _API_PREFIXES):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(categories.router)
    app.include_router(transactions.router)
    app.include_router(summary.router)
    app.include_router(budgets.router)
    app.include_router(insights.router)
    app.include_router(assistant.router)

    _serve_web(app)
    return app


def _serve_web(app: FastAPI) -> None:
    """Serve the built React SPA when WEB_DIR is set (single-service deploy).

    Registered AFTER the API routers so /health, /budgets, ... still match first.
    Any other GET path returns the matching static file, or index.html (SPA routing).
    """
    web_dir = os.environ.get("WEB_DIR")
    if not web_dir or not os.path.isdir(web_dir):
        return
    web_root = os.path.abspath(web_dir)
    index = os.path.join(web_root, "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str) -> FileResponse:
        target = os.path.abspath(os.path.join(web_root, full_path))
        if full_path and target.startswith(web_root + os.sep) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(index)


app = create_app()
