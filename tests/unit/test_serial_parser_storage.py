import os
import tempfile
from unittest.mock import MagicMock, patch

from pi_log.serial_reader import SerialReader
from pi_log.storage import (
    initialize_db,
    insert_reading,
    get_unpushed_readings,
)


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    initialize_db(tmp.name)
    return tmp.name


@patch("pi_log.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial):
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    db_path = create_temp_db()

    def handler(parsed):
        insert_reading(db_path, parsed)

    reader = SerialReader("/dev/ttyUSB0", handler)
    reader.run()

    rows = get_unpushed_readings(db_path)
    os.unlink(db_path)

    assert len(rows) == 1
    assert rows[0]["cps"] == 9
