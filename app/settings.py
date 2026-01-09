# filename: app/settings.py

from __future__ import annotations
from typing import Any, Dict, Optional


class Section:
    """Wrap a dict so attributes work: section.key instead of section['key']"""

    def __init__(self, data: Optional[Dict[str, Any]]) -> None:
        self._data: Dict[str, Any] = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self) -> str:
        return repr(self._data)


class Settings:
    """
    Wrap the dict returned by load_config() into attribute-accessible sections.
    """

    def __init__(self, raw: Optional[Dict[str, Any]]) -> None:
        raw = raw or {}
        self.serial = Section(raw.get("serial", {}))
        self.sqlite = Section(raw.get("sqlite", {}))
        self.api = Section(raw.get("api", {}))
        self.push = Section(raw.get("push", {}))
        self.ingestion = Section(raw.get("ingestion", {}))
        self.telemetry = Section(raw.get("telemetry", {}))

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Settings":
        return cls(raw)

    def __repr__(self) -> str:
        return (
            f"Settings(serial={self.serial}, "
            f"sqlite={self.sqlite}, "
            f"api={self.api}, "
            f"push={self.push}, "
            f"ingestion={self.ingestion})"
        )
