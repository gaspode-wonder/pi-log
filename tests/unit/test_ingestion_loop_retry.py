from unittest.mock import patch


@patch("app.ingestion.csv_parser.parse_geiger_csv")
@patch("app.sqlite_store.SQLiteStore")
@patch("app.api_client.APIClient")
def test_ingestion_loop_handles_push_failure(mock_api, mock_store, mock_parse, loop_factory):
    # Mock parser output
    mock_parse.return_value = {"cps": 10}

    # Mock DB insert
    mock_store.return_value.insert_record.return_value = 1

    # Mock API failure
    mock_api_instance = mock_api.return_value
    mock_api_instance.push_record.side_effect = Exception("network error")

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "https://api.example", "token": "TOKEN"},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    loop.store = mock_store.return_value
    loop.api = mock_api_instance
    loop.api_enabled = True

    ok = loop.process_line("RAW_LINE")
    assert ok is True  # ingestion should log and continue, not crash
