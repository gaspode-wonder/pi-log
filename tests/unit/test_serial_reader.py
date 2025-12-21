import pytest
from unittest.mock import MagicMock, patch

from pi_log.serial_reader import SerialReader


@patch("pi_log.serial_reader.serial.Serial")
def test_serial_reader_reads_lines(mock_serial):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 10, CPM, 100, uSv/hr, 0.10, SLOW\n",
        b"CPS, 20, CPM, 200, uSv/hr, 0.20, FAST\n",
        KeyboardInterrupt,  # stop loop
    ]
    mock_serial.return_value = mock_port

    collected = []

    def fake_handler(parsed):
        collected.append(parsed)

    reader = SerialReader("/dev/ttyUSB0", fake_handler)
    reader.run()

    assert len(collected) == 2
    assert collected[0]["cps"] == 10
    assert collected[1]["cps"] == 20


@patch("pi_log.serial_reader.serial.Serial")
def test_serial_reader_skips_malformed_lines(mock_serial):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"INVALID LINE\n",
        b"CPS, 5, CPM, 50, uSv/hr, 0.05, INST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    collected = []

    def fake_handler(parsed):
        collected.append(parsed)

    reader = SerialReader("/dev/ttyUSB0", fake_handler)
    reader.run()

    assert len(collected) == 1
    assert collected[0]["cps"] == 5
