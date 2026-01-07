# pi-log/app/config_loader.py
from typing import Union
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.9 fallback


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = Path("/opt/pi-log/config.toml")


def load_config(path: Union[str, os.PathLike] = DEFAULT_CONFIG_PATH) -> dict:
    """
    Load a TOML config file and return a dict.

    Behavior required by tests:
      - If file exists and is valid TOML → return parsed dict.
      - If file missing → return {}.
      - If file unreadable → return {}.
      - If file malformed → return {}.
    """
    path = Path(path)

    if not path.exists():
        return {}

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
            return SettingsNamespace(data)
    except Exception:
        return {}


class SettingsNamespace:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, SettingsNamespace(value))
            else:
                setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)


# Tests expect CONFIG to exist at module level.
# It must NOT load /opt/pi-log/config.toml during import.
# So we return {} here, and runtime code loads real config explicitly.
CONFIG = {}
