# ADR demonstration backend

This FastAPI application implements the STORY-001 Mock identity entry flow and
the STORY-003 structured Draft creation flow.
Identity selection is intentionally not authentication and does not create an
access-control boundary.

Drafts are retained in the application process for this demonstration. They
capture the selected Mock identity as author, a distinct configured owner,
required decision context, one or more tags, and the demo-data boundary notice.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Test

```powershell
pytest
```
