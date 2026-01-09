# filename: tests/unit/test_logging_loader.py

from unittest.mock import patch
from app.logging import get_logger, setup_logging


@patch("logging.handlers.RotatingFileHandler._open", return_value=None)
@patch("app.logging.Path.mkdir")
def test_logger_initializes_without_error(mock_mkdir, mock_open):
    setup_logging()
    log = get_logger("test_logger")
    log.info("test message")
    assert log is not None
    assert mock_mkdir.called


@patch("logging.handlers.RotatingFileHandler._open", return_value=None)
@patch("app.logging.Path.mkdir")
def test_logger_multiple_calls_return_same_logger(mock_mkdir, mock_open):
    setup_logging()
    log1 = get_logger("test_logger")
    log2 = get_logger("test_logger")
    assert log1 is log2
    assert mock_mkdir.called
