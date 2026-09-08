from fastapi import FastAPI

from app.api.routes import health


def create_app() -> FastAPI:
    app = FastAPI(title="Internal Decision Record Application")
    app.include_router(health.router)
    return app


app = create_app()
