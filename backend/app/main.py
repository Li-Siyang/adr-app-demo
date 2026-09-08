from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes import health
from app.db.session import init_db


def create_app(initialize_schema: Callable[[], None] = init_db) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        initialize_schema()
        yield

    # The interactive documentation and schema endpoints are disabled because
    # they would let unauthenticated callers enumerate the protected API
    # surface (CR-NFR-002).
    app = FastAPI(
        title="Internal Decision Record Application",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.include_router(health.router)
    app.include_router(api_router)
    return app


app = create_app()
