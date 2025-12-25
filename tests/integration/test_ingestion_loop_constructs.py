from unittest.mock import patch

@patch("app.ingestion_loop.SerialReader")
def test_ingestion_loop_constructs(mock_reader, loop_factory):
    loop = loop_factory()
    assert loop.reader is not None
    assert loop.store is not None
    assert loop.poll_interval >= 0
    if loop.api_enabled:
        assert loop.api is not None
