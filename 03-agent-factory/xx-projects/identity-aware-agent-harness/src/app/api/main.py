from fastapi import FastAPI

from app.api.rate_limiter import InMemoryRateLimiter
from app.api.routes_identity import router as identity_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_tools import router as tools_router


def create_app() -> FastAPI:
    """Create the FastAPI application."""

    app = FastAPI(
        title="Identity-Aware Stateful Agent Harness",
        version="0.1.0",
    )
    app.state.rate_limiter = InMemoryRateLimiter()

    app.include_router(identity_router)
    app.include_router(tasks_router)
    app.include_router(tools_router)

    return app


app = create_app()
