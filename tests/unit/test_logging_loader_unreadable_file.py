from unittest.mock import patch
from app.logging_loader import get_logger


@patch("app.logging.os.path.exists", return_value=True)
@patch("app.logging.open", side_effect=OSError("cannot read file"))
@patch("app.logging.logging.config.dictConfig")
def test_logging_fallback_when_config_unreadable(mock_dict_config, _mock_open, _mock_exists):
    """
    If logging.toml exists but cannot be read, the loader should fall back
    to console-only logging and not raise an exception.
    """
    log = get_logger("unreadable_config_test")
    assert log is not None
    assert mock_dict_config.called
