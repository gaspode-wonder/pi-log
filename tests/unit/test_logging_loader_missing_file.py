from unittest.mock import patch
from app.logging_loader import get_logger


@patch("app.logging.os.path.exists", return_value=False)
@patch("app.logging.logging.config.dictConfig")
def test_logging_fallback_when_config_missing(mock_dict_config, _):
    """
    If logging.toml does not exist, the loader should fall back to
    console-only logging and not raise an exception.
    """
    log = get_logger("missing_config_test")
    assert log is not None
    assert mock_dict_config.called
