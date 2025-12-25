import sqlite3
from pathlib import Path
from datetime import datetime
from app.logging import get_logger

log = get_logger("pi-log")


class SQLiteStore:
    def __init__(self, db_path: str):
        print(">>> SQLiteStore INIT db_path =", db_path) # <-- ADD THIS
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def initialize_db(self):
        """Create the readings table if it does not exist."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cps REAL NOT NULL,
                cpm REAL NOT NULL,
                usv REAL NOT NULL,
                mode TEXT NOT NULL,
                raw TEXT NOT NULL,
                pushed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.conn.commit()


    def insert_record(self, record: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            timestamp = record.get("timestamp") or datetime.utcnow().isoformat()

            cur = conn.execute(
                """
                INSERT INTO readings (timestamp, cps, cpm, usv, mode, raw)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    record["cps"],
                    record["cpm"],
                    record["usv"],
                    record["mode"],
                    record.get("raw", ""),
                ),
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

        conn = sqlite3.connect(self.db_path)
        try:
            conn.executemany(
                "UPDATE readings SET pushed = 1 WHERE id = ?",
                [(i,) for i in ids],
            )
            conn.commit()
        finally:
            conn.close()


    def select_unpushed_readings(self):
        """
        Return all readings where pushed == 0 as a list of dicts.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(
                """
                SELECT id, timestamp, cps, cpm, usv, mode, raw, pushed
                FROM readings
                WHERE pushed = 0
                ORDER BY id ASC
                """
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()


    def mark_readings_pushed(self, ids):
        """
        Mark the given reading IDs as pushed.
        """
        if not ids:
            return

        conn = sqlite3.connect(self.db_path)
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
        conn = sqlite3.connect(self.db_path)
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
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM readings").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_latest_reading(self):
        query = """
            SELECT id, timestamp, cps, cpm, mode, raw
            FROM readings
            ORDER BY id DESC
            LIMIT 1
        """
        cur = self.conn.execute(query)
        row = cur.fetchone()
        return dict(row) if row else None

    def get_recent_readings(self, limit: int = 10):
        query = """
            SELECT id, timestamp, cps, cpm, mode, raw
            FROM readings
            ORDER BY id DESC
            LIMIT ?
        """
        cur = self.conn.execute(query, (limit,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def count_readings(self):
        query = "SELECT COUNT(*) AS count FROM readings"
        cur = self.conn.execute(query)
        row = cur.fetchone()
        return row["count"] if row else 0
