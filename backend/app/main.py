from os import getenv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.api import router as api_router
from app.audit import AuditEventStore
from app.records import DecisionRecordStore
from app.tags import TagStore

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_AUDIT_DATABASE = Path(__file__).parents[1] / "data" / "audit.sqlite3"
APPLICATION_ENVIRONMENTS = {"development", "production"}


def create_app(
    audit_database_path: str | Path = DEFAULT_AUDIT_DATABASE,
    *,
    environment: str | None = None,
) -> FastAPI:
    if environment is None:
        environment = getenv("APP_ENV", "development")
    if environment not in APPLICATION_ENVIRONMENTS:
        raise ValueError(
            "APP_ENV must be either 'development' or 'production'."
        )

    app = FastAPI(title="Internal Decision Record Application")
    if environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)

    app.state.audit_event_store = AuditEventStore(audit_database_path)
    app.state.record_store = DecisionRecordStore()
    app.state.tag_store = TagStore()
    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def entry_screen() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/app", include_in_schema=False)
    def application_screen() -> FileResponse:
        return FileResponse(STATIC_DIR / "app.html")

    return app


app = create_app()
