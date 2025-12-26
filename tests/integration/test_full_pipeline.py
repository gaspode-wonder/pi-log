import os
import tempfile
from unittest.mock import patch
import responses

def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name

@patch("time.sleep", return_value=None)
@patch("app.ingestion.serial_reader.SerialReader")
@responses.activate
def test_full_pipeline(mock_reader, _, loop_factory):
    db_path = create_temp_db()

    mock_reader.return_value.read_line.side_effect = [
        "CPS, 7, CPM, 70, uSv/hr, 0.07, FAST",
        KeyboardInterrupt,
    ]

    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": db_path},
        "api": {"enabled": True, "base_url": "http://example.com/api", "token": "TOKEN"},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    os.unlink(db_path)
