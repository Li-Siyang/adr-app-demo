# ADR demonstration backend

This FastAPI application implements the STORY-001 Mock identity entry flow.
Identity selection is intentionally not authentication and does not create an
access-control boundary.

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

