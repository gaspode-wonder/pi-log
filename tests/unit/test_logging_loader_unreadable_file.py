# filename: tests/unit/test_logging_loader_unreadable_file.py

from unittest.mock import patch
from app.logging import get_logger, setup_logging


@patch("logging.handlers.RotatingFileHandler._open", return_value=None)
@patch("app.logging.Path.mkdir")
def test_logging_initialization_when_config_unreadable(mock_mkdir, mock_open_handler):
    """
    The new logging system does not read config files at all.
    Even if a file were unreadable, logging must still initialize cleanly.
    """
    setup_logging()
    log = get_logger("unreadable_config_test")
    log.info("test message")

    assert log is not None
    assert mock_mkdir.called
