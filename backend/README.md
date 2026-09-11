# ADR demonstration backend

This FastAPI application implements the STORY-001 Mock identity entry flow,
the STORY-003 structured Draft creation flow, and STORY-009 exact-tag record
discovery. STORY-015 provides append-only audit-event storage and read-only
retrieval for governed actions.
Identity selection is intentionally not authentication and does not create an
access-control boundary.

Drafts are retained in the application process for this demonstration. They
capture the selected Mock identity as author, a distinct configured owner,
required decision context, one or more tags, and the demo-data boundary notice.
Users operating under a selected Mock identity can list all retained records or
apply one exact tag filter. Tag discovery does not exclude records based on
lifecycle or archival condition.
Audit events are durably retained in `backend/data/audit.sqlite3` with the
acting Mock identity, timestamp, subject, and immutable field-level changes.
The existing approver designation flow records these events; later governed
workflows can use the same audit store.

Decision records and approver designations are process-local demonstration
state, so this MVP must run as a single application process (the default
`uvicorn app.main:app` invocation). Do not deploy multiple workers: governance
state would diverge between workers even though audit history is shared.

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
