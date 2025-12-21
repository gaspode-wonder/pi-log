import sqlite3
from datetime import datetime
from app.logging_loader import get_logger

log = get_logger(__name__)


class SQLiteStore:
    """
    Encapsulates all SQLite operations:
      - DB initialization
      - inserting readings
      - retrieving unpushed readings
      - marking readings as pushed
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        """Internal helper to open a connection with row_factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create the readings table if it doesn't exist."""
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cps INTEGER,
                cpm INTEGER,
                usv REAL,
                mode TEXT,
                pushed INTEGER DEFAULT 0
            )
            """
        )

        conn.commit()
        conn.close()
        log.debug("SQLite database initialized")

    def insert_record(self, reading: dict) -> int:
        """Insert a parsed reading into the database and return its ID."""
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO readings (timestamp, cps, cpm, usv, mode)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                reading["cps"],
                reading["cpm"],
                reading["usv"],
                reading["mode"],
            ),
        )

        conn.commit()
        record_id = cur.lastrowid
        conn.close()

        log.debug(f"Inserted reading {record_id}")
        return record_id

    def get_unpushed_readings(self):
        """Return all readings where pushed = 0."""
        conn = self._connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT * FROM readings
            WHERE pushed = 0
            ORDER BY id ASC
            """
        )

        rows = cur.fetchall()
        conn.close()
        return rows

    def mark_readings_pushed(self, ids: list[int]):
        """Mark a list of reading IDs as pushed."""
        if not ids:
            return

        conn = self._connect()
        cur = conn.cursor()

        placeholders = ",".join("?" for _ in ids)

        cur.execute(
            f"""
            UPDATE readings
            SET pushed = 1
            WHERE id IN ({placeholders})
            """,
            ids,
        )

        conn.commit()
        conn.close()
        log.debug(f"Marked readings pushed: {ids}")
