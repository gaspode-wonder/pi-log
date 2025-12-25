import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from app.settings import Settings
from app.ingestion_loop import IngestionLoop
from app.sqlite_store import SQLiteStore

# ---------------------------------------------------------------------------
# GLOBAL SAFETY PATCH: SerialReader is ALWAYS mocked
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_serial_reader():
    """
    Ensures no test ever instantiates a real SerialReader.
    Applies to ALL tests automatically.
    """
    with patch("app.ingestion_loop.SerialReader") as mock_reader:
        mock_reader.return_value = MagicMock()
        yield

# ---------------------------------------------------------------------------
# SETTINGS FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_settings():
    return Settings.from_dict({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": False},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })


@pytest.fixture
def temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        yield tmp.name
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


@pytest.fixture
def temp_db_settings(temp_db):
    return Settings.from_dict({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": temp_db},
        "api": {"enabled": False},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })


# ---------------------------------------------------------------------------
# LOOP FACTORY — SIMPLE, SAFE, NO PATCHING
# ---------------------------------------------------------------------------

@pytest.fixture
def loop_factory(fake_settings):
    """
    Returns a function that constructs a fresh IngestionLoop(fake_settings).
    Tests patch SerialReader themselves when needed.
    """
    def _factory(settings_override=None):
        settings = (
            Settings.from_dict(settings_override)
            if settings_override else fake_settings
        )
        return IngestionLoop(settings)

    return _factory


# ---------------------------------------------------------------------------
# READER FACTORY
# ---------------------------------------------------------------------------

@pytest.fixture
def reader_factory():
    def _factory(lines):
        mock_reader = MagicMock()
        mock_reader.read_line.side_effect = lines
        return mock_reader
    return _factory


# ---------------------------------------------------------------------------
# FAKE API + STORE
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_api():
    class FakeAPI:
        def __init__(self):
            self.calls = []

        def push_record(self, record_id, record):
            self.calls.append((record_id, record))

    return FakeAPI()


@pytest.fixture
def fake_store(temp_db):
    store = SQLiteStore(temp_db)
    store.initialize_db()
    return store
