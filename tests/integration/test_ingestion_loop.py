import app.ingestion_loop as ingestion_loop

def make_fake_record():
    return {"cps": 10, "cpm": 100, "usv": 0.1, "mode": "FAST"}


def test_process_line_happy_path(monkeypatch, loop_factory):
    calls = {}

    def fake_parse(raw):
        calls["parse_raw"] = raw
        return make_fake_record()

    class FakeStore:
        def __init__(self, *args, **kwargs):
            pass
        def insert_record(self, record):
            calls["store_record"] = record
            return 123
        def mark_readings_pushed(self, ids):
            calls["mark_pushed_ids"] = ids

    def fake_record_ingestion(record):
        calls["metrics_record"] = record

    class FakeAPIClient:
        def __init__(self, base_url, token):
            calls["api_init"] = (base_url, token)
        def push_record(self, record_id, record):
            calls["api_push"] = (record_id, record)

    class FakeLogExpClient:
        def __init__(self, base_url, token):
            calls["logexp_init"] = (base_url, token)
        def push(self, record_id, record):
            calls["logexp_push"] = (record_id, record)

    monkeypatch.setattr("app.ingestion.csv_parser.parse_geiger_csv", fake_parse)
    monkeypatch.setattr("app.sqlite_store.SQLiteStore", FakeStore)
    monkeypatch.setattr("app.metrics.record_ingestion", fake_record_ingestion)
    monkeypatch.setattr("app.api_client.APIClient", FakeAPIClient)
    monkeypatch.setattr("app.logexp_client.LogExpClient", FakeLogExpClient)

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "https://api.example", "token": "TOKEN"},
        "push": {"enabled": True, "url": "https://logexp", "api_key": "KEY"},
        "ingestion": {"poll_interval": 0.0},
    })

    ok = loop.process_line("RAW_LINE")
    assert ok is True
    assert calls["parse_raw"] == "RAW_LINE"
    assert "store_record" in calls
    assert "metrics_record" in calls
    assert "api_push" in calls
    assert "logexp_push" in calls


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

    monkeypatch.setattr("app.ingestion.serial_reader.SerialReader", FakeReader)

    loop = loop_factory()
    monkeypatch.setattr(loop, "process_line", fake_process_line)

    result = loop.run_once()
    assert result is True
    assert calls["read_line"] is True
    assert calls["process_line_raw"] == "RAW"
