# filename: app/api_client.py

from __future__ import annotations

import sqlite3
import requests
from datetime import datetime, timezone
from typing import Any, Dict

from app.models import GeigerRecord


class PushClient:
    """
    PushClient is the ingestion engine:
      - receives parsed records via handle_record()
      - writes them to SQLite
      - pushes them immediately to the ingestion API
      - marks them pushed on success
    """

    def __init__(
        self, api_url: str, api_token: str, device_id: str, db_path: str
    ) -> None:
        if not api_url:
            raise ValueError("PushClient requires a non-empty api_url")

        self.ingest_url = api_url
        self.api_token = api_token or ""
        self.device_id = device_id
        self.db_path = db_path

        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")

    # ------------------------------------------------------------
    # SQLite helpers
    # ------------------------------------------------------------

    def _insert_record(self, parsed: Dict[str, Any]) -> int:
        """
        Insert a parsed geiger record into SQLite.
        Returns the inserted row ID.
        """

        timestamp = parsed.get("timestamp") or datetime.now(timezone.utc)

        cur = self._conn.cursor()
        cur.execute(
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                parsed["raw"],
                parsed["cps"],
                parsed["cpm"],
                parsed["usv"],
                parsed["mode"],
                self.device_id,
                timestamp.isoformat(),
            ),
        )
        self._conn.commit()

        rowid = cur.lastrowid
        assert rowid is not None
        return rowid

    def _mark_pushed(self, row_id: int) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE geiger_readings SET pushed = 1 WHERE id = ?",
            (row_id,),
        )
        self._conn.commit()

    # ------------------------------------------------------------
    # Push logic
    # ------------------------------------------------------------

    def _push_single(self, record: GeigerRecord) -> bool:
        """
        Push a single GeigerRecord to the ingestion endpoint.
        Returns True on success.
        """
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            resp = requests.post(
                self.ingest_url, json=record.to_logexp_payload(), headers=headers
            )
            resp.raise_for_status()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------
    # Public callback for SerialReader
    # ------------------------------------------------------------

    def handle_record(self, parsed: Dict[str, Any]) -> None:
        """
        Called by SerialReader for every parsed record.
        """

        row_id = self._insert_record(parsed)

        timestamp = parsed.get("timestamp") or datetime.now(timezone.utc)

        record = GeigerRecord(
            id=row_id,
            raw=parsed["raw"],
            counts_per_second=parsed["cps"],
            counts_per_minute=parsed["cpm"],
            microsieverts_per_hour=parsed["usv"],
            mode=parsed["mode"],
            device_id=self.device_id,
            timestamp=timestamp,
        )

        if self._push_single(record):
            self._mark_pushed(row_id)
