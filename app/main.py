from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import time
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, HttpUrl


DB_PATH = Path(os.getenv("STATUSPULSE_DB_PATH", Path(__file__).resolve().parent.parent / "statuspulse.sqlite3"))
app = FastAPI(title="StatusPulse", version="0.1.0")
STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl


def connection() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize() -> None:
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                status_code INTEGER,
                latency_ms INTEGER NOT NULL,
                error TEXT,
                checked_at TEXT NOT NULL,
                FOREIGN KEY (monitor_id) REFERENCES monitors(id) ON DELETE CASCADE
            );
            """
        )


initialize()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_INDEX)


@app.get("/monitors")
def list_monitors() -> list[dict]:
    with connection() as db:
        rows = db.execute("SELECT * FROM monitors ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


@app.post("/monitors", status_code=201)
def create_monitor(payload: MonitorCreate) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        cursor = db.execute(
            "INSERT INTO monitors (name, url, created_at) VALUES (?, ?, ?)",
            (payload.name, str(payload.url), created_at),
        )
        monitor_id = cursor.lastrowid
    return {"id": monitor_id, "name": payload.name, "url": str(payload.url), "created_at": created_at}


def run_check(monitor_id: int, url: str) -> dict:
    started = time.perf_counter()
    status = "up"
    status_code = None
    error = None
    try:
        request = Request(url, headers={"User-Agent": "StatusPulse/0.1"})
        with urlopen(request, timeout=10) as response:
            status_code = response.status
            if status_code >= 400:
                status = "down"
    except HTTPError as exc:
        status = "down"
        status_code = exc.code
        error = str(exc.reason)
    except (URLError, TimeoutError, OSError) as exc:
        status = "down"
        error = str(exc)
    latency_ms = round((time.perf_counter() - started) * 1000)
    checked_at = datetime.now(timezone.utc).isoformat()
    with connection() as db:
        db.execute(
            "INSERT INTO checks (monitor_id, status, status_code, latency_ms, error, checked_at) VALUES (?, ?, ?, ?, ?, ?)",
            (monitor_id, status, status_code, latency_ms, error, checked_at),
        )
    return {
        "monitor_id": monitor_id,
        "status": status,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "error": error,
        "checked_at": checked_at,
    }


@app.post("/monitors/{monitor_id}/checks")
def check_monitor(monitor_id: int) -> dict:
    with connection() as db:
        monitor = db.execute("SELECT * FROM monitors WHERE id = ?", (monitor_id,)).fetchone()
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return run_check(monitor_id, monitor["url"])


@app.get("/monitors/{monitor_id}/history")
def monitor_history(monitor_id: int, limit: int = 20) -> list[dict]:
    with connection() as db:
        monitor_exists = db.execute("SELECT 1 FROM monitors WHERE id = ?", (monitor_id,)).fetchone()
        if monitor_exists is None:
            raise HTTPException(status_code=404, detail="Monitor not found")
        rows = db.execute(
            "SELECT * FROM checks WHERE monitor_id = ? ORDER BY id DESC LIMIT ?",
            (monitor_id, min(max(limit, 1), 100)),
        ).fetchall()
    return [dict(row) for row in rows]
