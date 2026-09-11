# ADR demonstration backend

This FastAPI application implements the STORY-001 Mock identity entry flow,
the STORY-003 structured Draft creation flow, the STORY-004 author editing
and guarded Draft submission flow, and STORY-009 exact-tag record discovery.
Identity selection is intentionally not authentication and does not create an
access-control boundary.

Drafts are retained in the application process for this demonstration. They
capture the selected Mock identity as author, a distinct configured owner,
required decision context, one or more tags, and the demo-data boundary notice.
Authors can edit their own eligible Drafts. Submission changes a complete,
non-abandoned Draft to Proposed only when at least one designated approver
exists.
Users operating under a selected Mock identity can list all retained records or
apply one exact tag filter. Tag discovery does not exclude records based on
lifecycle or archival condition.

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
