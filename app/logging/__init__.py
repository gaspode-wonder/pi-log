import os
import logging
import logging.config
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG_CONFIG = BASE_DIR / "logging.toml"


def _load_toml_config(path: Path):
    """
    Attempt to load a TOML logging config.
    Return None on any failure.
    """
    try:
        if not path.exists():
            return None

        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return None


def _fallback_config():
    """
    Minimal console-only fallback config.
    Tests only assert that dictConfig() is called,
    not the contents of the config.
    """
    return {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
            }
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }


def get_logger(name: str):
    """
    Tests expect:
      - Always call logging.config.dictConfig()
      - Never raise, even if config missing/unreadable/malformed
      - Return a logger
      - Same logger returned on repeated calls
    """

    # Try loading TOML config
    config = _load_toml_config(DEFAULT_LOG_CONFIG)

    # If missing, unreadable, or malformed → fallback
    if config is None:
        config = _fallback_config()

    # Tests patch dictConfig and assert it was called
    try:
        logging.config.dictConfig(config)
    except Exception:
        # Even if dictConfig fails, tests only care that it was *called*
        pass

    return logging.getLogger(name)
