from unittest.mock import patch

import app.ingestion_loop as ingestion_loop


@patch("app.metrics.record_ingestion")
@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
def test_metrics_recorded(mock_store, mock_parse, mock_record, loop_factory):
    mock_parse.return_value = {"cps": 10}
    mock_store.return_value.insert_record.return_value = 1

    loop = loop_factory()

    loop.process_line("RAW_LINE")

    mock_record.assert_called_once_with({"cps": 10})
