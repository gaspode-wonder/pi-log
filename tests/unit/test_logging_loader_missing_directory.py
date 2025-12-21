from unittest.mock import patch
from app.logging_loader import get_logger


@patch("app.logging.os.path.exists", return_value=False)
@patch("app.logging.logging.config.dictConfig")
def test_logging_fallback_when_log_directory_missing(mock_dict_config, _):
    """
    If the logging config references a file handler whose directory does not exist,
    the loader should fall back to console logging and not raise an exception.
    """
    log = get_logger("fallback_test_logger")
    assert log is not None
    assert mock_dict_config.called
