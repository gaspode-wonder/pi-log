# filename: tests/integration/test_ingestion_with_mock_serial.py

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.serial_reader.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv  # noqa: F401
from app.sqlite_store import insert_record, get_unpushed_records
from app.models import GeigerRecord


@patch("app.serial_reader.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial, temp_db):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    calls = []

    def fake_handler(parsed_dict):
        calls.append(parsed_dict)

        record = GeigerRecord(
            id=None,
            raw=parsed_dict.get("raw", ""),
            counts_per_second=parsed_dict["cps"],
            counts_per_minute=parsed_dict["cpm"],
            microsieverts_per_hour=parsed_dict["usv"],
            mode=parsed_dict["mode"],
            device_id="test-device",
            timestamp=datetime.now(timezone.utc),
            pushed=False,
        )

        insert_record(temp_db, record)

    reader = SerialReader("/dev/ttyUSB0")

    with patch.object(reader, "_handle_parsed", side_effect=fake_handler):
        reader.run()

    # Validate handler was called
    assert len(calls) == 1
    assert calls[0]["cps"] == 9

    # Validate record was stored
    stored = get_unpushed_records(temp_db)
    assert len(stored) == 1
    assert stored[0].counts_per_second == 9
