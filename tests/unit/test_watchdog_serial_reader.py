# filename: tests/unit/test_watchdog_serial_reader.py

import time
import pytest

from app.ingestion.watchdog import WatchdogSerialReader


class MockSerial:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class MockReader:
    def __init__(self, lines=None, raise_on_call=False):
        self.lines = lines or []
        self.raise_on_call = raise_on_call
        self.calls = 0
        self.handler = None
        self.ser = MockSerial()

    def set_handler(self, handler):
        self.handler = handler

    def read_line(self):
        self.calls += 1
        if self.raise_on_call:
            raise RuntimeError("boom")
        if self.lines:
            return self.lines.pop(0)
        return ""



def test_watchdog_proxies_set_handler():
    mock = MockReader()
    wd = WatchdogSerialReader(mock)

    def handler(_):
        pass

    wd.set_handler(handler)

    assert mock.handler is handler


def test_watchdog_updates_last_frame_timestamp_on_data():
    mock = MockReader(lines=["abc"])
    wd = WatchdogSerialReader(mock)

    before = wd._last_frame_ts
    time.sleep(0.01)

    line = wd.read_line()

    assert line == "abc"
    assert wd._last_frame_ts > before


def test_watchdog_triggers_reopen_on_exception(monkeypatch):
    mock = MockReader(raise_on_call=True)
    wd = WatchdogSerialReader(mock)

    reopened = {"called": False}

    def fake_reopen():
        reopened["called"] = True

    monkeypatch.setattr(wd, "_reopen", fake_reopen)

    # read_line should catch the exception and call _reopen()
    with pytest.raises(RuntimeError):
        # second call after reopen will still raise, so we expect the error
        wd.read_line()

    assert reopened["called"] is True


def test_watchdog_triggers_reopen_on_dead_link(monkeypatch):
    mock = MockReader(lines=[""])
    wd = WatchdogSerialReader(mock, dead_threshold_seconds=0.0)

    reopened = {"called": False}

    def fake_reopen():
        reopened["called"] = True

    monkeypatch.setattr(wd, "_reopen", fake_reopen)

    wd.read_line()

    assert reopened["called"] is True
