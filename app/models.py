# filename: app/models.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class GeigerRecord:
    """
    Canonical local representation of a single Geiger reading in Pi-log.

    This is the shape we store in SQLite and use as the source for pushes
    to LogExp. It keeps the raw MightyOhm CSV line for debugging and
    diagnostics, but the wire contract with LogExp uses only the canonical
    ingestion fields (no raw or local timestamp).

    Fields:
        id: Optional database primary key (None before insert).
        raw: Exact MightyOhm CSV line as read from the serial device.
        counts_per_second: CPS value parsed from the CSV.
        counts_per_minute: CPM value parsed from the CSV.
        microsieverts_per_hour: uSv/hr value parsed from the CSV.
        mode: One of "SLOW", "FAST", or "INST".
        device_id: Logical identifier for this Pi-log node (e.g. "pi-log").
        timestamp: UTC timestamp recorded locally when the reading was created.
        pushed: Whether this reading has been successfully pushed to LogExp.
    """

    id: Optional[int]
    raw: str
    counts_per_second: int
    counts_per_minute: int
    microsieverts_per_hour: float
    mode: str
    device_id: str
    timestamp: datetime
    pushed: bool = False

    # ------------------------------------------------------------
    # Generic dict serializer (used by PushClient)
    # ------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    # ------------------------------------------------------------
    # Construct from parsed CSV
    # ------------------------------------------------------------
    @classmethod
    def from_parsed(
        cls,
        parsed: dict[str, Any],
        device_id: str = "pi-log",
        timestamp: Optional[datetime] = None,
    ) -> GeigerRecord:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        return cls(
            id=None,
            raw=str(parsed["raw"]),
            counts_per_second=int(parsed["cps"]),
            counts_per_minute=int(parsed["cpm"]),
            microsieverts_per_hour=float(parsed["usv"]),
            mode=str(parsed["mode"]),
            device_id=device_id,
            timestamp=timestamp,
            pushed=False,
        )

    # ------------------------------------------------------------
    # Payload for LogExp ingestion API
    # ------------------------------------------------------------
    def to_logexp_payload(self) -> dict[str, Any]:
        return {
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode.upper(),
            "device_id": self.device_id,
        }

    # ------------------------------------------------------------
    # SQLite row mapping
    # ------------------------------------------------------------
    def to_db_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "raw": self.raw,
            "counts_per_second": self.counts_per_second,
            "counts_per_minute": self.counts_per_minute,
            "microsieverts_per_hour": self.microsieverts_per_hour,
            "mode": self.mode,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "pushed": 1 if self.pushed else 0,
        }

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> GeigerRecord:
        ts_raw = row.get("timestamp")

        if isinstance(ts_raw, str):
            timestamp = datetime.fromisoformat(ts_raw)
        elif isinstance(ts_raw, datetime):
            timestamp = ts_raw
        else:
            timestamp = datetime.now(timezone.utc)

        return cls(
            id=row.get("id"),
            raw=row["raw"],
            counts_per_second=int(row["counts_per_second"]),
            counts_per_minute=int(row["counts_per_minute"]),
            microsieverts_per_hour=float(row["microsieverts_per_hour"]),
            mode=row["mode"],
            device_id=row["device_id"],
            timestamp=timestamp,
            pushed=bool(row.get("pushed", 0)),
        )
