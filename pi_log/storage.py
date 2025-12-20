import sqlite3
from datetime import datetime


def initialize_db(db_path: str):
    conn = sqlite3.connect(db_path)
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


def insert_reading(db_path: str, reading: dict):
    conn = sqlite3.connect(db_path)
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
    conn.close()


def get_unpushed_readings(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
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


def mark_readings_pushed(db_path: str, ids: list[int]):
    if not ids:
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        f"""
        UPDATE readings
        SET pushed = 1
        WHERE id IN ({','.join('?' for _ in ids)})
        """,
        ids,
    )

    conn.commit()
    conn.close()
