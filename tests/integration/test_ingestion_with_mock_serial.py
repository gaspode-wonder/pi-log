from unittest.mock import patch, MagicMock
from app.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

@patch("app.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial, fake_store):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    store = fake_store

    def fake_handler():
        raw = mock_port.readline().decode("utf-8").strip()
        parsed = parse_geiger_csv(raw)
        if parsed:
            store.insert_record(parsed)

    with patch.object(SerialReader, "run", side_effect=fake_handler):
        reader = SerialReader("/dev/ttyUSB0")
        reader.run()
