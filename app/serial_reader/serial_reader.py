# filename: app/serial_reader/serial_reader.py

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional
import serial

from app.ingestion.csv_parser import parse_geiger_csv


ParsedRecord = Dict[str, Any]
ParsedHandler = Callable[[ParsedRecord], None]


class SerialReader:
    """
    Reads raw lines from a serial device, parses them, and forwards parsed
    records to a callback set by the ingestion loop.
    """

    def __init__(self, device: str, baudrate: int = 9600, timeout: float = 1.0) -> None:
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout

        self.ser: Optional[serial.Serial] = None
        self._handle_parsed: Optional[ParsedHandler] = None

    def read_line(self) -> str:
        """
        Read a single line from the serial device.
        Returns a decoded UTF-8 string or an empty string on timeout.
        """
        if self.ser is None:
            self.ser = serial.Serial(
                self.device,
                self.baudrate,
                timeout=self.timeout,
            )

        raw = self.ser.readline()
        if not raw:
            return ""

        decoded: str = raw.decode("utf-8", errors="ignore").strip()
        return decoded

    def run(self) -> None:
        """
        Continuously read lines, parse them, and forward parsed records.
        """
        while True:
            try:
                raw = self.read_line()
                parsed = parse_geiger_csv(raw)

                if parsed is not None and self._handle_parsed is not None:
                    self._handle_parsed(parsed)

            except (KeyboardInterrupt, StopIteration):
                break

            except Exception:
                time.sleep(0.1)
