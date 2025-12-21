import os
import tempfile
from unittest.mock import MagicMock, patch
import responses

from pi_log.geiger_reader import GeigerReader


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


@patch("pi_log.serial_reader.serial.Serial")
@responses.activate
def test_full_pipeline(mock_serial):
    db_path = create_temp_db()

    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 7, CPM, 70, uSv/hr, 0.07, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    responses.add(
        responses.POST,
        "http://example.com/api/ingest",
        json={"status": "ok"},
        status=200,
    )

    reader = GeigerReader(
        device_path="/dev/ttyUSB0",
        db_path=db_path,
        api_url="http://example.com/api/ingest",
        api_token="TOKEN",
        push_interval=0,
    )

    reader.run()

    # If no exceptions occurred, the pipeline is functioning
    os.unlink(db_path)
