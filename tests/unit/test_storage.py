import sqlite3

from app.sqlite_store import SQLiteStore


def test_initialize_db_creates_schema(temp_db):
    store = SQLiteStore(temp_db)
    store.initialize_db()

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='readings'")
    result = cur.fetchone()
    conn.close()

    assert result is not None


def test_insert_and_select_unpushed(fake_store):
    store = fake_store

    reading = {
        "cps": 10,
        "cpm": 100,
        "usv": 0.10,
        "mode": "SLOW",
    }

    record_id = store.insert_record(reading)
    assert isinstance(record_id, int)

    unpushed = store.select_unpushed_readings()
    assert len(unpushed) == 1
    assert unpushed[0]["id"] == record_id


def test_mark_readings_pushed(fake_store):
    store = fake_store

    reading = {
        "cps": 5,
        "cpm": 50,
        "usv": 0.05,
        "mode": "FAST",
    }

    record_id = store.insert_record(reading)

    unpushed_before = store.select_unpushed_readings()
    assert any(r["id"] == record_id for r in unpushed_before)

    store.mark_readings_pushed([record_id])

    unpushed_after = store.select_unpushed_readings()
    assert all(r["id"] != record_id for r in unpushed_after)
