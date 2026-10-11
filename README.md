# StatusPulse

StatusPulse is a lightweight uptime monitoring API for websites and services. It stores monitored endpoints and check history in SQLite, measures response time, and exposes a small REST API that can power a dashboard.

## Features

- Register and list monitored URLs
- Run an on-demand availability check
- Track status code, latency, and errors
- Persist history with SQLite
- Health endpoint for deployment checks
- Automated tests for the core API flow

## Run locally

```bash
python -m venv .venv
\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/monitors` | List monitors |
| POST | `/monitors` | Create a monitor |
| POST | `/monitors/{id}/checks` | Run a check |
| GET | `/monitors/{id}/history` | Read check history |

## Quality goals

The project favors explicit boundaries, small endpoints, deterministic persistence, and tests that cover the user-facing workflow.
