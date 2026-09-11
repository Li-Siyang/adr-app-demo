from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.audit import AuditEventStore
from app.records import DecisionRecordStore

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_AUDIT_DATABASE = Path(__file__).parents[1] / "data" / "audit.sqlite3"


def create_app(
    audit_database_path: str | Path = DEFAULT_AUDIT_DATABASE,
) -> FastAPI:
    app = FastAPI(title="Internal Decision Record Application")
    app.state.audit_event_store = AuditEventStore(audit_database_path)
    app.state.record_store = DecisionRecordStore()
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
