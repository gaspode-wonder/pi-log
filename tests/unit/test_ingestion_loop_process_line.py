from unittest.mock import patch


@patch("app.ingestion.csv_parser.parse_geiger_csv")
@patch("app.sqlite_store.SQLiteStore")
@patch("app.api_client.APIClient")
def test_process_line_stores_and_pushes(mock_api, mock_store, mock_parse, loop_factory):
    # Mock parser output
    mock_parse.return_value = {"cps": 10, "cpm": 100, "usv": 0.1, "mode": "FAST"}

    # Mock store behavior
    mock_store.return_value.insert_record.return_value = 1

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "https://api.example", "token": "TOKEN"},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    loop.store = mock_store.return_value
    loop.api = mock_api.return_value
    loop.api_enabled = True

    ok = loop.process_line("RAW_LINE")

    assert ok is True
    mock_store.return_value.insert_record.assert_called_once()
    mock_api.return_value.push_record.assert_called_once()
