# filename: tests/unit/test_serial_reader.py

import pytest  # noqa: F401
from unittest.mock import MagicMock, patch

from app.ingestion.serial_reader import SerialReader


@patch("app.ingestion.serial_reader.parse_geiger_csv")
@patch("app.ingestion.serial_reader.serial.Serial")
def test_serial_reader_reads_lines(mock_serial, mock_parse):
    # Mock serial port returning two valid lines then stopping
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 10, CPM, 100, uSv/hr, 0.10, SLOW\n",
        b"CPS, 20, CPM, 200, uSv/hr, 0.20, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    # Mock parser outputs
    mock_parse.side_effect = [
        {"cps": 10},
        {"cps": 20},
    ]

    reader = SerialReader("/dev/ttyUSB0")

    # Patch the internal handler SerialReader uses after parsing
    with patch.object(reader, "_handle_parsed") as mock_handler:
        reader.run()

    # Should have been called twice with parsed dicts
    assert mock_handler.call_count == 2
    assert mock_handler.call_args_list[0].args[0]["cps"] == 10
    assert mock_handler.call_args_list[1].args[0]["cps"] == 20


@patch("app.ingestion.serial_reader.parse_geiger_csv")
@patch("app.ingestion.serial_reader.serial.Serial")
def test_serial_reader_skips_malformed_lines(mock_serial, mock_parse):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"INVALID LINE\n",
        b"CPS, 5, CPM, 50, uSv/hr, 0.05, INST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    # First parse returns None (malformed), second returns valid dict
    mock_parse.side_effect = [
        None,
        {"cps": 5},
    ]

    reader = SerialReader("/dev/ttyUSB0")

    with patch.object(reader, "_handle_parsed") as mock_handler:
        reader.run()

    # Only the valid line should be handled
    assert mock_handler.call_count == 1
    assert mock_handler.call_args.args[0]["cps"] == 5
