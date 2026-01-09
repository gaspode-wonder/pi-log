# filename: app/logging_telemetry.py

"""
Telemetry handler for pi-log.

This module provides a non-blocking, queue-based telemetry pipeline
that can be attached to the logging subsystem as an additional sink.

Features:
- Structured JSON events
- Non-blocking ingestion (queue)
- Background worker thread
- Batching for efficiency
- Retry with exponential backoff
- Graceful failure (never blocks ingestion)
- Config-driven enable/disable
"""

import logging
import queue
import threading
import time
from datetime import datetime
from typing import Dict, Any, List

import requests


class TelemetryWorker(threading.Thread):
    """
    Background worker that drains the telemetry queue and sends batches
    to the configured telemetry endpoint.
    """

    def __init__(
        self,
        q: queue.Queue[dict[str, Any]],
        base_url: str,
        token: str,
        batch_size: int = 20,
        max_backoff: float = 30.0,
    ):
        super().__init__(daemon=True)
        self.q = q
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.batch_size = batch_size
        self.max_backoff = max_backoff
        self._stop_flag = False

    def stop(self) -> None:
        self._stop_flag = True

    def run(self) -> None:
        backoff = 1.0

        while not self._stop_flag:
            try:
                batch = self._drain_batch()
                if not batch:
                    time.sleep(0.1)
                    continue

                ok = self._send_batch(batch)
                if ok:
                    backoff = 1.0
                else:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, self.max_backoff)

            except Exception:
                # Never crash the worker
                time.sleep(1.0)

    def _drain_batch(self) -> List[Dict[str, Any]]:
        items: list[dict[str, Any]] = []
        try:
            while len(items) < self.batch_size:
                item = self.q.get_nowait()
                items.append(item)
        except queue.Empty:
            pass
        return items

    def _send_batch(self, batch: List[Dict[str, Any]]) -> bool:
        url = f"{self.base_url}/telemetry"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(url, json=batch, headers=headers, timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False


class TelemetryHandler(logging.Handler):
    """
    Logging handler that pushes structured log events into a telemetry queue.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        level: int = logging.INFO,
        batch_size: int = 20,
    ):
        super().__init__(level)

        # Explicit type annotation required by mypy
        self.q: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=5000)

        self.worker = TelemetryWorker(
            q=self.q,
            base_url=base_url,
            token=token,
            batch_size=batch_size,
        )
        self.worker.start()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            event = self._record_to_event(record)
            self.q.put_nowait(event)
        except queue.Full:
            # Drop telemetry if queue is full
            pass
        except Exception:
            # Never break logging
            pass

    def _record_to_event(self, record: logging.LogRecord) -> Dict[str, Any]:
        event: dict[str, Any] = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Include structured extras
        for key, value in record.__dict__.items():
            if key not in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ):
                event[key] = value

        return event

    def close(self) -> None:
        try:
            self.worker.stop()
        except Exception:
            pass
        super().close()
