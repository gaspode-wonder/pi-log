from unittest.mock import patch, mock_open
from app.logging_loader import get_logger


@patch("app.logging.os.path.exists", return_value=True)
@patch("app.logging.open", new_callable=mock_open, read_data="not: valid: toml")
@patch("app.logging.tomllib.load", side_effect=Exception("malformed TOML"))
@patch("app.logging.logging.config.dictConfig")
def test_logging_fallback_when_config_malformed(mock_dict_config, _mock_toml, _mock_open, _mock_exists):
    """
    If logging.toml exists but contains invalid TOML, the loader should fall back
    to console-only logging and not raise an exception.
    """
    log = get_logger("malformed_config_test")
    assert log is not None
    assert mock_dict_config.called
