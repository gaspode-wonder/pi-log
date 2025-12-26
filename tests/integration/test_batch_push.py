from unittest.mock import patch

def test_batch_push_sequential(loop_factory):
    with patch("app.ingestion.csv_parser.parse_geiger_csv") as mock_parse, \
         patch("app.sqlite_store.SQLiteStore") as mock_store, \
         patch("app.api_client.APIClient") as mock_api:

        mock_parse.side_effect = [{"cps": 1}, {"cps": 2}, {"cps": 3}]
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
