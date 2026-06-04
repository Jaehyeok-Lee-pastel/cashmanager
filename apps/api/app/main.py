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


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
