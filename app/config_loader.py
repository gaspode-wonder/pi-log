# filename: app/config_loader.py

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Dict, Union


DEFAULT_CONFIG_PATH = Path("config.toml")


class SettingsNamespace:
    """
    Recursive namespace wrapper for config dictionaries.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, SettingsNamespace(value))
            else:
                setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getattr__(self, name: str) -> None:
        raise AttributeError(f"No such config section: {name}")


def load_config(
    path: Union[str, Path] = DEFAULT_CONFIG_PATH,
) -> Union[Dict[str, Any], SettingsNamespace]:
    """
    Load a TOML config file.

    Test contract:
    - Missing file → return {}
    - Unreadable/malformed file → return {}
    - Valid file → return SettingsNamespace
    """
    path = Path(path)
    print(">>> loading:", path)

    if not path.exists():
        return {}

    try:
        with path.open("rb") as f:
            data: Any = tomllib.load(f)
            print(">>> parsed:", data)

    except Exception:
        return {}

    result: Union[Dict[str, Any], SettingsNamespace]

    if isinstance(data, dict):
        result = SettingsNamespace(data)
    else:
        result = {}

    return result
