from unittest.mock import patch

import app.ingestion_loop as ingestion_loop


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_retry_logic_api_failure(mock_api, mock_store, mock_parse, loop_factory):
    # Parser returns valid reading
    mock_parse.return_value = {"cps": 10}

    # DB insert returns ID
    mock_store.return_value.insert_record.return_value = 1

    # API always fails
    mock_api_instance = mock_api.return_value
    mock_api_instance.push_record.side_effect = Exception("network down")

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True, "base_url": "http://example.com", "token": "TOKEN"},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    loop.store = mock_store.return_value
    loop.api = mock_api_instance
    loop.api_enabled = True

    ok = loop.process_line("RAW_LINE")
    assert ok is True  # ingestion shouldn't blow up even if API fails
