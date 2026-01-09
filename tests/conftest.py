# filename: tests/conftest.py

import os  # noqa: F401
import sqlite3
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.api import app, get_store
from app.settings import Settings
from app.sqlite_store import initialize_db, insert_record
from app.api_client import PushClient
from app.models import GeigerRecord


# ---------------------------------------------------------------------------
# GLOBAL: Mock SerialReader so no test touches real hardware
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_serial_reader():
    # Patch the canonical serial reader path
    with patch("app.serial_reader.serial_reader.SerialReader") as mock_reader:
        mock_reader.return_value = MagicMock()
        yield


# ---------------------------------------------------------------------------
# SETTINGS FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_settings(tmp_path):
    db_path = tmp_path / "test.db"
    return Settings.from_dict(
        {
            "serial": {"device": "/dev/fake", "baudrate": 9600},
            "sqlite": {"path": str(db_path)},
            "api": {"enabled": False},
            "push": {"enabled": False},
            "ingestion": {"poll_interval": 0.0},
        }
    )


# ---------------------------------------------------------------------------
# SQLITE FIXTURES (canonical geiger_readings only)
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_db(str(db_path))
    return str(db_path)


@pytest.fixture
def db_with_records(temp_db):
    def _loader(records):
        for rec in records:
            insert_record(temp_db, rec)
        return temp_db

    return _loader


# ---------------------------------------------------------------------------
# PUSH CLIENT FIXTURE
# ---------------------------------------------------------------------------


@pytest.fixture
def push_client():
    return PushClient(api_url="http://example.com", api_token="TOKEN")


# ---------------------------------------------------------------------------
# GEIGER RECORD FACTORY
# ---------------------------------------------------------------------------


@pytest.fixture
def geiger_record():
    def _factory(**overrides):
        base = {
            "raw": "RAW",
            "counts_per_second": 10,
            "counts_per_minute": 600,
            "microsieverts_per_hour": 0.10,
            "mode": "FAST",
            "device_id": "pi-log",
        }
        base.update(overrides)
        return GeigerRecord(**base)

    return _factory


# ---------------------------------------------------------------------------
# API TEST STORE + CLIENT FIXTURE
# ---------------------------------------------------------------------------


class _TestStore:
    """A minimal store wrapper for API tests."""

    def __init__(self, db_path):
        self.db_path = db_path
        initialize_db(db_path)

    def get_latest_reading(self):
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

    def get_recent_readings(self, limit=10):
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

    def count_readings(self):
        conn = sqlite3.connect(self.db_path)
        try:
            (count,) = conn.execute("SELECT COUNT(*) FROM geiger_readings").fetchone()
            return count
        finally:
            conn.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "api_test.db")
    store = _TestStore(db_path)

    def override_get_store():
        return store

    app.dependency_overrides[get_store] = override_get_store
    return TestClient(app)
