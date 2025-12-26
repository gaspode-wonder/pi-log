import time
from fastapi import Depends

from app.ingestion.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

import app.sqlite_store as sqlite_store
import app.metrics as metrics

from app.api_client import APIClient
from app.config_loader import load_config
from app.logging import get_logger, setup_logging
from app.logexp_client import LogExpClient
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
        self.reader = SerialReader(
            self.settings.serial.get("device", "/dev/ttyUSB0"),
            self.settings.serial.get("baudrate", 9600),
        )

        # SQLite store
        self.store = SQLiteStore(self.settings.sqlite.get("path", ":memory:"))

        # API client
        api_cfg = self.settings.api
        self.api_enabled = api_cfg.get("enabled", False)
        if self.api_enabled:
            self.api = APIClient(
                api_cfg.get("base_url", ""),
                api_cfg.get("token", ""),
            )
        else:
            self.api = None

        # LogExp client
        push_cfg = self.settings.push
        self.logexp_enabled = push_cfg.get("enabled", False)
        if self.logexp_enabled:
            self.logexp = LogExpClient(
                base_url=push_cfg.get("url", ""),
                token=push_cfg.get("api_key", ""),
            )
        else:
            self.logexp = None

        self.poll_interval = self.settings.ingestion.get("poll_interval", 1)

        # Wire callback
        self.reader._handle_parsed = self._handle_parsed

    # ----------------------------------------------------------------------
    def _ingest_record(self, record):
        try:
            record_id = self.store.insert_record(record)

            metrics.record_ingestion(record)

            if self.api:
                try:
                    self.api.push_record(record_id, record)
                    if hasattr(self.store, "mark_readings_pushed"):
                        self.store.mark_readings_pushed([record_id])
                except Exception as exc:
                    self.logger.error(f"API push failed: {exc}")

            if self.logexp:
                try:
                    self.logexp.push(record_id, record)
                except Exception as exc:
                    self.logger.error(f"LogExp push failed: {exc}")

            return True

        except Exception as exc:
            self.logger.error(f"_ingest_record failed: {exc}")
            return False

    # ----------------------------------------------------------------------
    def process_line(self, raw):
        self.logger.debug(f"PROCESSING RAW: {raw!r}")

        try:
            record = parse_geiger_csv(raw)

            if record is None:
                self.logger.warning("parse_geiger_csv returned no record")
                return False

            return self._ingest_record(record)

        except Exception as exc:
            self.logger.error(f"process_line failed: {exc}")
            return False

    # ----------------------------------------------------------------------
    def _handle_parsed(self, record):
        try:
            ok = self._ingest_record(record)
            if not ok:
                self.logger.warning("_handle_parsed: ingestion failed")
        except Exception as exc:
            self.logger.error(f"_handle_parsed failed: {exc}")

    # ----------------------------------------------------------------------
    def run_once(self):
        try:
            raw = self.reader.read_line()
            ok = self.process_line(raw)
            if not ok:
                self.logger.warning("run_once: ingestion failed")
        except Exception as exc:
            self.logger.error(f"run_once failed: {exc}")
        return True

    # ----------------------------------------------------------------------
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


def build_ingestion_loop(settings: Settings = Depends(get_settings)):
    return IngestionLoop(settings)


def main():
    setup_logging()
    raw = load_config("/opt/pi-log/config.toml")
    settings = Settings.from_dict(raw)
    loop = IngestionLoop(settings)
    loop.run_forever()


if __name__ == "__main__":
    main()
