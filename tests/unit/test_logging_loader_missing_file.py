# filename: tests/unit/test_logging_loader_missing_file.py

from unittest.mock import patch
from app.logging import get_logger, setup_logging


@patch("logging.handlers.RotatingFileHandler._open", return_value=None)
@patch("app.logging.Path.mkdir")
def test_logging_initialization_when_config_missing(mock_mkdir, mock_open_handler):
    """
    The new logging system does not load or check for any external config file.
    Logging must initialize cleanly and produce a usable logger.
    """
    setup_logging()
    log = get_logger("missing_config_test")
    log.info("test message")

    assert log is not None
    assert mock_mkdir.called
