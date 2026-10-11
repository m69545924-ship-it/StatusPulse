# StatusPulse

[![CI](https://github.com/m69545924-ship-it/StatusPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/m69545924-ship-it/StatusPulse/actions/workflows/ci.yml)

StatusPulse is a lightweight uptime monitoring API for websites and services. It stores monitored endpoints and check history in SQLite, measures response time, and exposes a small REST API that can power a dashboard.

## Features

- Register and list monitored URLs
- Run an on-demand availability check
- Track status code, latency, and errors
- Persist history with SQLite
- Health endpoint for deployment checks
- Automated tests with GitHub Actions
- Docker and Docker Compose support

## Run locally

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API documentation at:

`http://127.0.0.1:8000/docs`

## Run with Docker

```bash
docker compose up --build
```

The API and interactive documentation will be available at:

`http://127.0.0.1:8000/docs`

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

## License

This project is licensed under the MIT License.
