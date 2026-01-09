# filename: tests/unit/test_logging_loader_malformed_toml.py

from unittest.mock import patch, mock_open
from app.logging import get_logger, setup_logging


@patch("logging.handlers.RotatingFileHandler._open", return_value=None)
@patch("app.logging.Path.mkdir")
@patch("app.logging.open", new_callable=mock_open, read_data="not: valid: toml")
def test_logging_fallback_when_config_malformed(_mock_open_file, mock_mkdir, mock_open_handler):
    setup_logging()
    log = get_logger("malformed_config_test")
    log.info("test message")
    assert log is not None
    assert mock_mkdir.called
