from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    return app


app = create_app()
