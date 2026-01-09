from pathlib import Path  # noqa: F401

from app.config_loader import load_config, SettingsNamespace
from app.settings import Settings


def test_load_config_missing_file_returns_empty_dict(tmp_path):
    missing = tmp_path / "does_not_exist.toml"
    result = load_config(missing)
    assert result == {}


def test_load_config_valid_toml(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [serial]
        device = "/dev/ttyUSB0"
        baudrate = 9600
    """
    )

    result = load_config(config_path)
    assert isinstance(result, SettingsNamespace)
    assert result.serial.device == "/dev/ttyUSB0"
    assert result.serial.baudrate == 9600


def test_settings_from_dict():
    raw = {
        "serial": {"device": "/dev/ttyUSB0", "baudrate": 9600},
        "sqlite": {"path": "test.db"},
        "ingestion": {"poll_interval": 1},
    }

    settings = Settings.from_dict(raw)

    assert settings.serial.device == "/dev/ttyUSB0"
    assert settings.sqlite.path == "test.db"
    assert settings.ingestion.poll_interval == 1
