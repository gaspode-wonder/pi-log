import os
import sqlite3
import tempfile
from pi_log.storage import (
    initialize_db,
    insert_reading,
    get_unpushed_readings,
    mark_readings_pushed,
)


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    initialize_db(tmp.name)
    return tmp.name


def test_initialize_db_creates_schema():
    db_path = create_temp_db()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='readings'")
    result = cur.fetchone()

    conn.close()
    os.unlink(db_path)

    assert result is not None


def test_insert_and_select_unpushed():
    db_path = create_temp_db()

    reading = {
        "cps": 10,
        "cpm": 100,
        "usv": 0.10,
        "mode": "SLOW",
    }

    insert_reading(db_path, reading)
    rows = get_unpushed_readings(db_path)

    os.unlink(db_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["cps"] == 10
    assert row["cpm"] == 100
    assert row["usv"] == 0.10
    assert row["mode"] == "SLOW"
    assert row["pushed"] == 0


def test_mark_readings_pushed():
    db_path = create_temp_db()

    reading = {
        "cps": 5,
        "cpm": 50,
        "usv": 0.05,
        "mode": "FAST",
    }

    insert_reading(db_path, reading)
    rows = get_unpushed_readings(db_path)
    ids = [row["id"] for row in rows]

    mark_readings_pushed(db_path, ids)

    rows_after = get_unpushed_readings(db_path)

    os.unlink(db_path)

    assert len(rows_after) == 0
