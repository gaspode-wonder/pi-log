import logging
import logging.config
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def get_logger(name: str):
    """
    Loads logging configuration from TOML.
    If the file handler path does not exist (e.g., on macOS),
    fall back to a safe console-only config.
    """
    config_path = Path("/opt/pi-log/config/logging.toml")

    # Local dev fallback
    if not config_path.exists():
        config_path = Path("config/logging.toml")

    try:
        with config_path.open("rb") as f:
            config = tomllib.load(f)

        # Validate file handler path
        for handler in config.get("handlers", {}).values():
            if "filename" in handler:
                log_path = Path(handler["filename"])
                if not log_path.parent.exists():
                    # Local dev fallback: console logging
                    raise FileNotFoundError

        logging.config.dictConfig(config)

    except Exception:
        # Safe fallback for macOS/local dev
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    return logging.getLogger(name)
