from unittest.mock import patch


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_ingestion_loop_pushes_multiple_records(mock_api, mock_store, mock_parse, loop_factory):
    # Mock parser output for multiple lines
    mock_parse.side_effect = [
        {"cps": 1},
        {"cps": 2},
        {"cps": 3},
    ]

    # Mock DB insert IDs
    mock_store.return_value.insert_record.side_effect = [1, 2, 3]

    loop = loop_factory({
        "serial": {"device": "/dev/fake", "baudrate": 9600},
        "sqlite": {"path": ":memory:"},
        "api": {"enabled": True},
        "push": {"enabled": False},
        "ingestion": {"poll_interval": 0.0},
    })

    loop.store = mock_store.return_value
    loop.api = mock_api.return_value
    loop.api_enabled = True

    loop.process_line("L1")
    loop.process_line("L2")
    loop.process_line("L3")

    assert mock_store.return_value.insert_record.call_count == 3
    assert mock_api.return_value.push_record.call_count == 3
