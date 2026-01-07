# app/ingestion/ingestion_loop.py

import time

import app.ingestion.serial_reader as serial_reader
import app.ingestion.csv_parser as csv_parser

import app.sqlite_store as sqlite_store
import app.metrics as metrics
import app.api_client as api_client
import app.logexp_client as logexp_client

from app.config_loader import load_config
from app.logging import get_logger, setup_logging
from app.settings import Settings

SQLiteStore = sqlite_store.SQLiteStore

log = get_logger("pi-log")


class IngestionLoop:
    """
    High-level ingestion orchestrator.
    """

    def __init__(self, settings: Settings):
        self.logger = log
        self.settings = settings

        # Serial reader
        reader_cls = serial_reader.SerialReader
        self.reader = reader_cls(
            self.settings.serial.get("device", "/dev/ttyUSB0"),
            self.settings.serial.get("baudrate", 9600),
        )

        # SQLite store
        self.store = sqlite_store.SQLiteStore(
            self.settings.sqlite.get("path", ":memory:")
        )

        # API client
        api_cfg = self.settings.api
        self.api_enabled = api_cfg.get("enabled", False)
        self.api = None
        if self.api_enabled:
            self.api = api_client.APIClient(
                api_cfg.get("base_url", ""),
                api_cfg.get("token", ""),
            )

        # LogExp client
        push_cfg = self.settings.push
        self.logexp_enabled = push_cfg.get("enabled", False)
        self.logexp = None
        if self.logexp_enabled:
            self.logexp = logexp_client.LogExpClient(
                base_url=push_cfg.get("url", ""),
                token=push_cfg.get("api_key", ""),
            )

        # Poll interval (normalize to float, safe fallback)
        raw_interval = self.settings.ingestion.get("poll_interval", 1)
        try:
            self.poll_interval = float(raw_interval)
        except Exception:
            self.poll_interval = 1.0

        # Wire callback
        self.reader._handle_parsed = self._handle_parsed

    # ------------------------------------------------------------------
    def _ingest_record(self, record):
        record_id = None

        try:
            record_id = self.store.insert_record(record)
        except Exception as exc:
            self.logger.error(f"DB insert failed: {exc}")

        # Metrics should ALWAYS fire if we parsed a record
        try:
            metrics.record_ingestion(record)
        except Exception as exc:
            self.logger.error(f"metrics failed: {exc}")

        if record_id is not None:
            if self.api:
                try:
                    self.api.push_record(record_id, record)
                    if hasattr(self.store, "mark_readings_pushed"):
                        self.store.mark_readings_pushed([record_id])
                except Exception as exc:
                    self.logger.error(f"API push failed: {exc}")

            if self.logexp_enabled and self.logexp:
                try:
                    self.logexp.push(record_id, record)
                except Exception as exc:
                    self.logger.error(f"LogExp push failed: {exc}")

        return True

    # ------------------------------------------------------------------
    def process_line(self, raw):
        self.logger.debug(f"PROCESSING RAW: {raw!r}")

        try:
            record = csv_parser.parse_geiger_csv(raw)

            if record is None:
                self.logger.warning("parse_geiger_csv returned no record")
                return True

            return self._ingest_record(record)

        except Exception as exc:
            self.logger.error(f"process_line failed: {exc}")
            return False

    # ------------------------------------------------------------------
    def _handle_parsed(self, record):
        try:
            ok = self._ingest_record(record)
            if not ok:
                self.logger.warning("_handle_parsed: ingestion failed")
        except Exception as exc:
            self.logger.error(f"_handle_parsed failed: {exc}")

    # ------------------------------------------------------------------
    def run_once(self):
        try:
            raw = self.reader.read_line()
            ok = self.process_line(raw)
            if not ok:
                self.logger.warning("run_once: ingestion failed")
        except Exception as exc:
            self.logger.error(f"run_once failed: {exc}")
        return True

    # ------------------------------------------------------------------
    def run_forever(self):
        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                break
            except Exception as exc:
                self.logger.error(f"run_forever iteration failed: {exc}")
            time.sleep(self.poll_interval)


# ----------------------------------------------------------------------
def get_settings() -> Settings:
    raw = load_config("/opt/pi-log/config.toml")
    return Settings.from_dict(raw)


def build_ingestion_loop(settings: Settings = None):
    if settings is None:
        settings = get_settings()
    return IngestionLoop(settings)


def main():
    setup_logging()
    raw = load_config("/opt/pi-log/config.toml")
    settings = Settings.from_dict(raw)
    loop = IngestionLoop(settings)
    loop.run_forever()


if __name__ == "__main__":
    main()
