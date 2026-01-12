# filename: app/api.py

from __future__ import annotations

import time
import sqlite3
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.sqlite_store import initialize_db


APP_START_TIME = time.time()
DB_PATH = "/var/lib/pi-log/readings.db"

app = FastAPI(title="Pi-Log API", version="0.1.0")


class HealthDBStatus(BaseModel):
    status: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    db: HealthDBStatus


class Reading(BaseModel):
    id: int
    timestamp: str
    cps: float
    cpm: float
    mode: str
    raw: Optional[str] = None


class MetricsResponse(BaseModel):
    ingested_count: int
    uptime_seconds: float
    version: str = "0.1.0"


class Store:
    """Canonical SQLite store wrapper for API use."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        initialize_db(db_path)

    def get_latest_reading(self) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                """
                SELECT id, raw, counts_per_second, counts_per_minute,
                       microsieverts_per_hour, mode, device_id,
                       timestamp, pushed
                FROM geiger_readings
                ORDER BY id DESC LIMIT 1
                """
            ).fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "raw": row[1],
                "cps": row[2],
                "cpm": row[3],
                "mode": row[5],
                "timestamp": row[7],
            }
        finally:
            conn.close()

    def get_recent_readings(self, limit: int) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """
                SELECT id, raw, counts_per_second, counts_per_minute,
                       microsieverts_per_hour, mode, device_id,
                       timestamp, pushed
                FROM geiger_readings
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [
                {
                    "id": r[0],
                    "raw": r[1],
                    "cps": r[2],
                    "cpm": r[3],
                    "mode": r[5],
                    "timestamp": r[7],
                }
                for r in rows
            ]
        finally:
            conn.close()

    def count_readings(self) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute("SELECT COUNT(*) FROM geiger_readings").fetchone()
            count = int(row[0])
            return count
        finally:
            conn.close()


def get_store() -> Store:
    return Store(DB_PATH)


def get_uptime_seconds() -> float:
    return time.time() - APP_START_TIME


@app.get("/health", response_model=HealthResponse)
def health(store: Store = Depends(get_store)) -> HealthResponse:
    uptime = get_uptime_seconds()
    db_status = "ok"
    db_error: Optional[str] = None

    try:
        store.get_latest_reading()
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)

    return HealthResponse(
        status="ok",
        uptime_seconds=uptime,
        db=HealthDBStatus(status=db_status, error=db_error),
    )


@app.get("/readings/latest", response_model=Reading)
def latest_reading(store: Store = Depends(get_store)) -> Reading:
    row = store.get_latest_reading()
    if not row:
        raise HTTPException(status_code=404, detail="No readings available")

    return Reading(**row)


@app.get("/readings", response_model=List[Reading])
def list_readings(
    limit: int = Query(10, ge=1, le=1000),
    store: Store = Depends(get_store),
) -> List[Reading]:
    rows = store.get_recent_readings(limit=limit)
    return [Reading(**row) for row in rows]


@app.get("/metrics", response_model=MetricsResponse)
def metrics(store: Store = Depends(get_store)) -> MetricsResponse:
    try:
        count = store.count_readings()
    except Exception:
        count = -1

    return MetricsResponse(
        ingested_count=count,
        uptime_seconds=get_uptime_seconds(),
    )
