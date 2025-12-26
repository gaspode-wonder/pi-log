from unittest.mock import patch

@patch("time.sleep", return_value=None)
@patch("app.ingestion.serial_reader.SerialReader")
def test_run_forever_one_iteration(mock_reader, _, loop_factory):
    mock_reader.return_value.read_line.side_effect = [
        "CPS, 5, CPM, 50, uSv/hr, 0.05, SLOW",
        KeyboardInterrupt,
    ]

    loop = loop_factory()

    with patch.object(loop, "process_line") as mock_process:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    mock_process.assert_called_once_with("CPS, 5, CPM, 50, uSv/hr, 0.05, SLOW")
