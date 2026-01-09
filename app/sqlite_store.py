# filename: app/sqlite_store.py

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List

from app.models import GeigerRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS geiger_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw TEXT NOT NULL,
    counts_per_second INTEGER NOT NULL,
    counts_per_minute INTEGER NOT NULL,
    microsieverts_per_hour REAL NOT NULL,
    mode TEXT NOT NULL,
    device_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    pushed INTEGER NOT NULL DEFAULT 0
);
"""


def initialize_db(db_path: str) -> None:
    """
    Initialize the SQLite database with the canonical schema only.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def insert_record(db_path: str, record: GeigerRecord) -> None:
    """
    Insert a new GeigerRecord into the canonical geiger_readings table.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO geiger_readings (
                raw,
                counts_per_second,
                counts_per_minute,
                microsieverts_per_hour,
                mode,
                device_id,
                timestamp,
                pushed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.raw,
                record.counts_per_second,
                record.counts_per_minute,
                record.microsieverts_per_hour,
                record.mode,
                record.device_id,
                record.timestamp.isoformat(),
                1 if record.pushed else 0,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _row_to_record(row: tuple) -> GeigerRecord:
    """
    Convert a SQLite row tuple into a GeigerRecord.
    """
    (
        id_,
        raw,
        cps,
        cpm,
        usv,
        mode,
        device_id,
        ts_raw,
        pushed,
    ) = row

    timestamp = (
        datetime.fromisoformat(ts_raw)
        if isinstance(ts_raw, str)
        else datetime.now(timezone.utc)
    )

    return GeigerRecord(
        id=id_,
        raw=raw,
        counts_per_second=int(cps),
        counts_per_minute=int(cpm),
        microsieverts_per_hour=float(usv),
        mode=mode,
        device_id=device_id,
        timestamp=timestamp,
        pushed=bool(pushed),
    )


def get_unpushed_records(db_path: str) -> List[GeigerRecord]:
    """
    Return all canonical records where pushed == 0.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                id,
                raw,
                counts_per_second,
                counts_per_minute,
                microsieverts_per_hour,
                mode,
                device_id,
                timestamp,
                pushed
            FROM geiger_readings
            WHERE pushed = 0
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        return [_row_to_record(row) for row in rows]
    finally:
        conn.close()


def mark_records_pushed(db_path: str, ids: List[int]) -> None:
    """
    Mark the given canonical record IDs as pushed.
    """
    if not ids:
        return

    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            "UPDATE geiger_readings SET pushed = 1 WHERE id = ?",
            [(i,) for i in ids],
        )
        conn.commit()
    finally:
        conn.close()
