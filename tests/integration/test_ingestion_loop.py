import app.ingestion_loop as ingestion_loop


def make_fake_record():
    return {"cpm": 42, "usv_per_h": 0.12, "timestamp": "2025-12-22T16:00:00Z"}


def test_process_line_happy_path(monkeypatch, loop_factory):
    calls = {}

    # Patch parser
    def fake_parse(raw):
        calls["parse_raw"] = raw
        return make_fake_record()

    # Patch store
    class FakeStore:
        def __init__(self, *args, **kwargs):
            pass
        def insert_record(self, record):
            calls["store_record"] = record
            return 123

        def mark_readings_pushed(self, ids):
            calls["mark_pushed_ids"] = ids

    # Patch metrics
    def fake_record_ingestion(record):
        calls["metrics_record"] = record

    # Patch API client
    class FakeAPIClient:
        def __init__(self, base_url, token):
            calls["api_init"] = (base_url, token)

        def push_record(self, record_id, record):
            calls["api_push"] = (record_id, record)

    # Patch LogExp client
    class FakeLogExpClient:
        def __init__(self, base_url, token):
            calls["logexp_init"] = (base_url, token)

        def push(self, record_id, record):
            calls["logexp_push"] = (record_id, record)

    # Wire patches
    monkeypatch.setattr(ingestion_loop, "parse_geiger_csv", fake_parse)
    monkeypatch.setattr(ingestion_loop, "SQLiteStore", FakeStore)
    monkeypatch.setattr(ingestion_loop.metrics, "record_ingestion", fake_record_ingestion)
    monkeypatch.setattr(ingestion_loop, "APIClient", FakeAPIClient)
    monkeypatch.setattr(ingestion_loop, "LogExpClient", FakeLogExpClient)

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "https://api.example", "token": "api-token"},
        "push": {"enabled": True, "url": "https://logexp.example", "api_key": "logexp-key"},
        "ingestion": {"poll_interval": 0.1},
    })

    ok = loop.process_line("RAW_LINE")

    assert ok is True
    assert calls["parse_raw"] == "RAW_LINE"
    assert "store_record" in calls
    assert "metrics_record" in calls
    assert "api_push" in calls
    assert "logexp_push" in calls
    assert calls["mark_pushed_ids"] == [123]


def test_process_line_malformed(monkeypatch, loop_factory):
    # Parser returns None -> should log and return False
    def fake_parse(raw):
        return None

    class FakeStore:
        def __init__(self, *args, **kwargs):
            pass
        def insert_record(self, record):
            raise AssertionError("Should not be called")

    monkeypatch.setattr(ingestion_loop, "parse_geiger_csv", fake_parse)
    monkeypatch.setattr(ingestion_loop, "SQLiteStore", FakeStore)

    loop = loop_factory()

    ok = loop.process_line("BAD_LINE")
    assert ok is False


def test_run_once_calls_process_line(monkeypatch, loop_factory):
    calls = {}

    class FakeReader:
        def __init__(self, *args, **kwargs):
            pass
        def read_line(self):
            calls["read_line"] = True
            return "RAW"

    def fake_process_line(raw):
        calls["process_line_raw"] = raw
        return True

    monkeypatch.setattr(ingestion_loop, "SerialReader", FakeReader)

    loop = loop_factory()
    monkeypatch.setattr(loop, "process_line", fake_process_line)

    result = loop.run_once()
    assert result is True
    assert calls["read_line"] is True
    assert calls["process_line_raw"] == "RAW"
