from fastapi import FastAPI
import uvicorn

from app.api.rate_limiter import InMemoryRateLimiter
from app.api.routes_identity import router as identity_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_tools import router as tools_router
from app.api.skill_routes import router as skill_router


def create_app() -> FastAPI:
    """FastAPI application."""

    app = FastAPI(
        title="Identity-Aware Stateful Agent Harness",
        version="0.1.0",
    )
    app.state.rate_limiter = InMemoryRateLimiter()

    app.include_router(identity_router)
    app.include_router(tasks_router)
    app.include_router(tools_router)
    app.include_router(skill_router)

    return app


app = create_app()

def main() -> None:
    uvicorn.run(
        app="app.api.main:app",
        reload=True,
        host="0.0.0.0",
        port=8000,
    )
    
if __name__=="__main__":
    main()
