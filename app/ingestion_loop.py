import time
from fastapi import Depends

# Import modules (not symbols) so tests can patch correctly
import app.serial_reader as serial_reader
import app.sqlite_store as sqlite_store
import app.metrics as metrics

from app.api_client import APIClient
from app.config_loader import load_config
from app.logging import get_logger, setup_logging
from app.logexp_client import LogExpClient
from app.settings import Settings

# Re-export names so tests can patch them via app.ingestion_loop.*
SerialReader = serial_reader.SerialReader
SQLiteStore = sqlite_store.SQLiteStore
parse_geiger_csv = serial_reader.parse_geiger_csv

log = get_logger("pi-log")


class IngestionLoop:
    """
    High-level ingestion orchestrator.

    Responsibilities:
      - Construct SerialReader, SQLiteStore, APIClient, LogExpClient
      - Provide process_line() for unit tests
      - Provide run_once() and run_forever()
      - Wire SerialReader._handle_parsed to ingestion logic
    """

    def __init__(self, settings: Settings):
        self.logger = log
        self.settings = settings

        # Serial reader (patched in tests)
        self.reader = SerialReader(
            self.settings.serial.get("device", "/dev/ttyUSB0"),
            self.settings.serial.get("baudrate", 9600),
        )

        # SQLite store (patched in tests)
        self.store = SQLiteStore(self.settings.sqlite.get("path", ":memory:"))

        # API client (optional)
        api_cfg = self.settings.api
        self.api_enabled = api_cfg.get("enabled", False)
        if self.api_enabled:
            self.api = APIClient(
                api_cfg.get("base_url", ""),
                api_cfg.get("token", ""),
            )
        else:
            self.api = None

        # LogExp client (optional)
        push_cfg = self.settings.push
        self.logexp_enabled = push_cfg.get("enabled", False)
        if self.logexp_enabled:
            self.logexp = LogExpClient(
                base_url=push_cfg.get("url", ""),
                token=push_cfg.get("api_key", ""),
            )
        else:
            self.logexp = None

        # Loop timing
        self.poll_interval = self.settings.ingestion.get("poll_interval", 1)

        # Wire SerialReader callback to ingestion logic
        self.reader._handle_parsed = self._handle_parsed

    # ----------------------------------------------------------------------
    # Core ingestion logic (shared by process_line and _handle_parsed)
    # ----------------------------------------------------------------------
    def _ingest_record(self, record):
        """
        Store, record metrics, and optionally push a parsed record.

        Returns True on success, False on failure.
        KeyboardInterrupt is always propagated.
        """
        try:
            # Storage
            record_id = self.store.insert_record(record)

            # Metrics
            metrics.record_ingestion(record)

            # Optional API push
            if self.api:
                try:
                    self.api.push_record(record_id, record)

                    if hasattr(self.store, "mark_readings_pushed"):
                        self.store.mark_readings_pushed([record_id])

                except KeyboardInterrupt:
                    raise
                except Exception as exc:
                    self.logger.error(f"API push failed: {exc}")

            # Optional LogExp push
            if self.logexp:
                try:
                    self.logexp.push(record_id, record)
                except KeyboardInterrupt:
                    raise
                except Exception as exc:
                    self.logger.error(f"LogExp push failed: {exc}")

            return True

        except KeyboardInterrupt:
            raise
        except Exception as exc:
            self.logger.error(f"_ingest_record failed: {exc}")
            return False

    # ----------------------------------------------------------------------
    # REQUIRED BY TESTS
    # ----------------------------------------------------------------------
    def process_line(self, raw):
        """
        Parse, store, record metrics, and optionally push a single raw line.
        Tests call this directly.

        Returns:
          True  - ingestion succeeded
          False - malformed line or ingestion failure
        """
        self.logger.debug(f"PROCESSING RAW: {raw!r}")

        try:
            record = parse_geiger_csv(raw)
            if not record:
                self.logger.warning("parse_geiger_csv returned no record")
                return False

            return self._ingest_record(record)

        except KeyboardInterrupt:
            raise
        except Exception as exc:
            self.logger.error(f"process_line failed: {exc}")
            return False

    # ----------------------------------------------------------------------
    # CALLED BY SerialReader.run()
    # ----------------------------------------------------------------------
    def _handle_parsed(self, record):
        """
        SerialReader calls this for each parsed record.
        """
        try:
            ok = self._ingest_record(record)
            if not ok:
                self.logger.warning("_handle_parsed: ingestion failed")
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            self.logger.error(f"_handle_parsed failed: {exc}")

    # ----------------------------------------------------------------------
    # TESTS EXPECT run_once() TO EXIST
    # ----------------------------------------------------------------------
    def run_once(self):
        """
        Read a single line from the serial reader and try to ingest it.

        Returns True to keep the contract simple for tests and callers.
        """
        try:
            raw = self.reader.read_line()
            ok = self.process_line(raw)
            if not ok:
                self.logger.warning("run_once: ingestion failed")
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            self.logger.error(f"run_once failed: {exc}")
        return True

    # ----------------------------------------------------------------------
    # TESTS EXPECT run_forever() TO LOOP UNTIL KeyboardInterrupt
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
# Dependency Injection entrypoints
# ----------------------------------------------------------------------
def get_settings() -> Settings:
    """FastAPI-style DI wrapper for ingestion settings."""
    raw = load_config("/opt/pi-log/config.toml")
    return Settings.from_dict(raw)


def build_ingestion_loop(
    settings: Settings = Depends(get_settings),
):
    """DI-friendly constructor for tests and runtime."""
    return IngestionLoop(settings)


def main():
    """
    Runtime entrypoint used by systemd.
    """
    setup_logging()
    raw = load_config("/opt/pi-log/config.toml")
    settings = Settings.from_dict(raw)
    loop = IngestionLoop(settings)
    loop.run_forever()


if __name__ == "__main__":
    main()
