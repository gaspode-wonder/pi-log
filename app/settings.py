# pi-log/app/settings.py
"""
Settings wrapper for ingestion loop and API.

load_config() returns a nested dict. This wrapper exposes attribute
access (settings.serial.device) while preserving dict semantics.
"""


class Section:
    """Wrap a dict so attributes work: section.key instead of section['key']"""
    def __init__(self, data: dict):
        self._data = data or {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self):
        return repr(self._data)


class Settings:
    """
    Wrap the dict returned by load_config() into attribute-accessible sections.
    """
    def __init__(self, raw: dict):
        raw = raw or {}
        self.serial = Section(raw.get("serial", {}))
        self.sqlite = Section(raw.get("sqlite", {}))
        self.api = Section(raw.get("api", {}))
        self.push = Section(raw.get("push", {}))
        self.ingestion = Section(raw.get("ingestion", {}))
        self.telemetry = Section(raw.get("telemetry", {}))


    @classmethod
    def from_dict(cls, raw: dict):
        return cls(raw)

    def __repr__(self):
        return (
            f"Settings(serial={self.serial}, "
            f"sqlite={self.sqlite}, "
            f"api={self.api}, "
            f"push={self.push}, "
            f"ingestion={self.ingestion})"
        )
