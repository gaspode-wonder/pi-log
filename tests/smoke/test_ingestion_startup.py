# tests/smoke/test_ingestion_startup.py

def test_ingestion_startup_smoke(monkeypatch):
    """
    Smoke test: ingestion loop should construct and run_once()
    without touching real serial, DB, or network.
    """

    # --------------------------------------------------------------
    # Fake config
    # --------------------------------------------------------------
    fake_config = {
        "serial": {"device": "/dev/null", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": False},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.01},
        "logging": {"level": "DEBUG", "log_dir": "/tmp"},
    }

    # --------------------------------------------------------------
    # Patch load_config to return fake config
    # --------------------------------------------------------------
    from app import config_loader
    monkeypatch.setattr(config_loader, "load_config", lambda path: fake_config)

    # --------------------------------------------------------------
    # Patch SerialReader to avoid hardware
    # --------------------------------------------------------------
    class FakeSerial:
        def read_line(self):
            return "123,456,789"

    monkeypatch.setattr(
        "app.ingestion.serial_reader.SerialReader",
        lambda *args, **kwargs: FakeSerial(),
    )

    # --------------------------------------------------------------
    # Patch SQLiteStore to avoid filesystem
    # --------------------------------------------------------------
    class FakeStore:
        def insert_record(self, record):
            return 1

    monkeypatch.setattr(
        "app.sqlite_store.SQLiteStore",
        lambda *args, **kwargs: FakeStore(),
    )

    # --------------------------------------------------------------
    # Patch metrics to avoid side effects
    # --------------------------------------------------------------
    import app.metrics as metrics
    monkeypatch.setattr(metrics, "record_ingestion", lambda record: None)

    # --------------------------------------------------------------
    # Construct and run_once
    # --------------------------------------------------------------
    from app.ingestion.ingestion_loop import IngestionLoop, Settings

    settings = Settings.from_dict(fake_config)
    loop = IngestionLoop(settings)

    assert loop.run_once() is True
