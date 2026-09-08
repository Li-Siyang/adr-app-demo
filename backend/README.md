# Backend

FastAPI backend for the Internal Decision Record Application.

## Setup

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
copy .env.example .env
```

## Run

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Test

```bash
.venv\Scripts\python.exe -m pytest
```

## Access control

Every route under `/api` requires a valid organizational SSO bearer token and an
active designated-team membership:

- missing or untrusted token -> `401`
- authenticated user who is not a designated team member -> `403`
- membership is read from storage on each request, so revoking
  `users.is_team_member` denies access on the very next request

`/health` is the only unauthenticated route and exposes no decision data.
