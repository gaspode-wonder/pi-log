from unittest.mock import patch, MagicMock
import sqlite3

from app.serial_reader import SerialReader
from app.csv_parser import parse_geiger_csv
from app.sqlite_store import SQLiteStore


@patch("app.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial, temp_db):
    # Mock the serial port to return one valid line, then stop
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,  # stop the reader loop
    ]
    mock_serial.return_value = mock_port

    store = SQLiteStore(temp_db)
    store.initialize_db()

    def fake_handler():
        raw = mock_port.readline().decode("utf-8").strip()
        parsed = parse_geiger_csv(raw)
        if parsed:
            store.insert_record(parsed)

    with patch.object(SerialReader, "run", side_effect=fake_handler):
        reader = SerialReader("/dev/ttyUSB0")
        reader.run()

    conn = sqlite3.connect(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM readings")
    count = cur.fetchone()[0]
    conn.close()

    assert count == 1
