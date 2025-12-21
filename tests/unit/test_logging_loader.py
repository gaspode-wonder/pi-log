from unittest.mock import patch, MagicMock
from app.logging_loader import get_logger


def test_logger_initializes_without_error():
    log = get_logger("test_logger")
    log.info("test message")
    assert log is not None


def test_logger_multiple_calls_return_logger():
    log1 = get_logger("test_logger")
    log2 = get_logger("test_logger")
    assert log1 is log2


@patch("app.logging.logging.config.dictConfig")
@patch("app.logging.os.path.exists")
def test_logging_fallback_when_log_directory_missing(mock_exists, mock_dict_config):
    """
    If the logging config references a file handler whose directory does not exist,
    the loader should fall back to console logging and not raise an exception.
    """

    # Simulate missing directory for file handler
    mock_exists.return_value = False

    # Call logger initialization
    log = get_logger("fallback_test_logger")

    # Should still return a logger object
    assert log is not None

    # dictConfig should still be called (with fallback config)
    assert mock_dict_config.called
