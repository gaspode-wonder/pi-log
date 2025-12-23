from typing import Union
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.9 fallback


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.toml"


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
            return tomllib.load(f)
    except Exception:
        return {}


# Tests expect CONFIG to exist at module level
CONFIG = load_config()
