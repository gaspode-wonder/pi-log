from unittest.mock import patch
import responses

@patch("time.sleep", return_value=None)
@patch("app.ingestion.serial_reader.SerialReader")
@patch("app.sqlite_store.SQLiteStore")
@responses.activate
def test_ingestion_loop_full_pipeline(mock_store, mock_reader, _, loop_factory):
    mock_reader.return_value.read_line.side_effect = [
        "CPS, 9, CPM, 90, uSv/hr, 0.09, FAST",
        KeyboardInterrupt,
    ]

    mock_store.return_value.insert_record.return_value = 1

    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "http://example.com/api", "token": "TOKEN"},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    loop.store = mock_store.return_value

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    mock_store.return_value.insert_record.assert_called_once()
