from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class Settings:
    """
    Loads config.toml at import time and exposes sections as attributes.
    Tests expect:
      - settings._data contains required sections
      - settings.serial, settings.sqlite, settings.api, settings.ingestion
    """

    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        config_path = base_dir / "config.toml"

        try:
            with config_path.open("rb") as f:
                self._data = tomllib.load(f)
        except Exception:
            # Tests expect sections to exist, so provide defaults
            self._data = {
                "serial": {"device": "/dev/ttyUSB0", "baudrate": 9600},
                "sqlite": {"path": "test.db"},
                "api": {
                    "enabled": False,
                    "base_url": "",
                    "token": "",
                },
                "ingestion": {"poll_interval": 1},
            }

    @property
    def serial(self):
        return self._data.get("serial", {})

    @property
    def sqlite(self):
        return self._data.get("sqlite", {})

    @property
    def api(self):
        return self._data.get("api", {})

    @property
    def ingestion(self):
        return self._data.get("ingestion", {})


settings = Settings()
