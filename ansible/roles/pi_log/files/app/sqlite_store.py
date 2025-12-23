import sqlite3
from pathlib import Path
from app.logging import get_logger

log = get_logger(__name__)


class SQLiteStore:
    """
    Minimal SQLite storage layer matching test expectations.

    Required behaviors:
      - insert_record(record) returns an integer ID
      - mark_readings_pushed([ids]) updates pushed flag
      - get_unpushed_readings() returns list of dicts
      - get_all_readings() returns list of dicts
      - automatically creates table if missing
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(self.path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cps INTEGER,
                    cpm INTEGER,
                    usv REAL,
                    mode TEXT,
                    pushed INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def insert_record(self, record: dict) -> int:
        """
        Insert a parsed record and return its ID.
        Tests patch this method and assert call counts.
        """
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute(
                """
                INSERT INTO readings (cps, cpm, usv, mode)
                VALUES (?, ?, ?, ?)
                """,
                (record["cps"], record["cpm"], record["usv"], record["mode"]),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def mark_readings_pushed(self, ids):
        """
        Mark readings as pushed.
        Tests patch this method and assert call counts.
        """
        if not ids:
            return

        conn = sqlite3.connect(self.path)
        try:
            conn.executemany(
                "UPDATE readings SET pushed = 1 WHERE id = ?",
                [(i,) for i in ids],
            )
            conn.commit()
        finally:
            conn.close()

    def get_unpushed_readings(self):
        """
        Return list of dicts for rows where pushed = 0.
        Tests expect dicts, not sqlite3.Row.
        """
        conn = sqlite3.connect(self.path)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM readings WHERE pushed = 0"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_all_readings(self):
        """
        Return list of dicts for all rows.
        """
        conn = sqlite3.connect(self.path)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM readings").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
