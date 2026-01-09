# pi-log/tests/integration/test_serial_to_parser_to_storage.py

from unittest.mock import patch, MagicMock
from app.serial_reader.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv  # noqa: F401
from app.sqlite_store import insert_record


@patch("app.serial_reader.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial, temp_db):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    calls = []

    def fake_handler(parsed):
        calls.append(parsed)
        insert_record(temp_db, parsed)

    reader = SerialReader("/dev/ttyUSB0")

    with patch.object(reader, "_handle_parsed", side_effect=fake_handler):
        reader.run()

    assert len(calls) == 1
    assert calls[0]["cps"] == 9
