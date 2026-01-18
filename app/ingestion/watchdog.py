# filename: app/ingestion/watchdog.py

import time
import logging
from typing import Any, Optional, Callable, Dict, Protocol

from app.ingestion.csv_parser import parse_geiger_csv

log = logging.getLogger(__name__)


class SerialReaderProtocol(Protocol):
    ser: Any

    def set_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        ...

    def read_line(self) -> str:
        ...


class WatchdogSerialReader:
    """
    Drop-in wrapper around a SerialReader-like object that adds:
      - dead-read detection
      - FTDI disappearance detection
      - automatic port reopen
    """

    def __init__(
        self,
        reader: SerialReaderProtocol,
        dead_threshold_seconds: float = 5.0,
        reopen_sleep_seconds: float = 2.0,
    ) -> None:
        self._reader: SerialReaderProtocol = reader
        self._dead_threshold = dead_threshold_seconds
        self._reopen_sleep = reopen_sleep_seconds
        self._last_frame_ts = time.time()
        self._handler: Optional[Callable[[Dict[str, Any]], None]] = None

    # ------------------------------------------------------------
    # Public API: must match SerialReader
    # ------------------------------------------------------------

    def set_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        self._handler = handler
        self._reader.set_handler(handler)

    def run(self) -> None:
        """
        Same loop as SerialReader.run(), but using watchdog-aware read_line().
        """
        while True:
            try:
                raw = self.read_line()
                log.info(f"RAW: {raw!r}")

                parsed = parse_geiger_csv(raw)
                log.info(f"PARSED: {parsed}")

                if parsed is not None and self._handler is not None:
                    self._handler(parsed)

            except (KeyboardInterrupt, StopIteration):
                break

            except Exception as exc:
                log.error(f"Error in watchdog serial loop: {exc}")
                time.sleep(0.1)

    # ------------------------------------------------------------
    # Watchdog logic
    # ------------------------------------------------------------

    def read_line(self) -> str:
        now = time.time()

        # Dead link detection
        if now - self._last_frame_ts > self._dead_threshold:
            log.warning(
                "watchdog_dead_link_detected",
                extra={"last_frame_age": now - self._last_frame_ts},
            )
            self._reopen()

        try:
            line = self._reader.read_line()
        except Exception as exc:
            log.error("watchdog_read_exception", extra={"error": repr(exc)})
            self._reopen()
            line = self._reader.read_line()

        if line:
            self._last_frame_ts = time.time()

        return line

    def _reopen(self) -> None:
        log.warning("watchdog_reopen_start")

        try:
            # Best-effort close with proper type narrowing
            ser = getattr(self._reader, "ser", None)
            if ser is not None:
                try:
                    ser.close()
                except Exception as exc:
                    log.error("watchdog_close_failed", extra={"error": repr(exc)})

            # Force lazy reopen
            self._reader.ser = None

            time.sleep(self._reopen_sleep)

            log.warning("watchdog_reopen_success")

        except Exception as exc:
            log.error("watchdog_reopen_failed", extra={"error": repr(exc)})
            raise
