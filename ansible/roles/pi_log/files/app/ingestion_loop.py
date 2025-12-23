import time

# Import modules (not symbols) so tests can patch correctly
import app.serial_reader as serial_reader
import app.sqlite_store as sqlite_store
import app.metrics as metrics

from app.api_client import APIClient
from app.config import settings
from app.logging import get_logger

# Re-export names so tests can patch them via app.ingestion_loop.*
SerialReader = serial_reader.SerialReader
SQLiteStore = sqlite_store.SQLiteStore
parse_geiger_csv = serial_reader.parse_geiger_csv

log = get_logger(__name__)


class IngestionLoop:
    """
    High-level ingestion orchestrator.

    Responsibilities:
      - Construct SerialReader, SQLiteStore, APIClient
      - Provide process_line() for unit tests
      - Provide run_once() and run_forever()
      - Wire SerialReader._handle_parsed to ingestion logic
    """

    def __init__(self):
        # Serial reader (patched in tests)
        self.reader = SerialReader(
            settings.serial.get("device", "/dev/ttyUSB0"),
            settings.serial.get("baudrate", 9600),
        )

        # SQLite store (patched in tests)
        self.store = SQLiteStore(settings.sqlite.get("path", ":memory:"))

        # API client
        api_cfg = settings.api
        self.api_enabled = api_cfg.get("enabled", False)
        self.api = APIClient(
            api_cfg.get("base_url", ""),
            api_cfg.get("token", ""),
        )

        # Loop timing
        self.poll_interval = settings.ingestion.get("poll_interval", 1)

        # Wire SerialReader callback to ingestion logic
        self.reader._handle_parsed = self._handle_parsed

    # ----------------------------------------------------------------------
    # REQUIRED BY TESTS
    # ----------------------------------------------------------------------
    def process_line(self, raw):
        """
        Parse, store, record metrics, and optionally push a single raw line.
        Tests call this directly.

        Fault tolerance:
          - Returns False on malformed or failed ingestion
          - KeyboardInterrupt always propagates
          - Other exceptions are logged and treated as failed ingestion
        """
        try:
            record = parse_geiger_csv(raw)
            if not record:
                return False

            # Storage
            record_id = self.store.insert_record(record)

            # Metrics
            metrics.record_ingestion(record)

            # Optional API push
            if self.api_enabled:
                try:
                    self.api.push_record(record_id, record)

                    if hasattr(self.store, "mark_readings_pushed"):
                        self.store.mark_readings_pushed([record_id])

                except KeyboardInterrupt:
                    # Do not swallow shutdown signals
                    raise
                except Exception as exc:
                    # Push failure should not kill ingestion
                    log.error(f"Push failed: {exc}")

            return True

        except KeyboardInterrupt:
            # Always propagate shutdown signals
            raise
        except Exception as exc:
            log.error(f"process_line failed: {exc}")
            return False

    # ----------------------------------------------------------------------
    # CALLED BY SerialReader.run()
    # ----------------------------------------------------------------------
    def _handle_parsed(self, record):
        """
        SerialReader calls this for each parsed record.

        Fault tolerance is similar to process_line(), but starts
        from an already-parsed record instead of raw text.
        """
        try:
            record_id = self.store.insert_record(record)

            metrics.record_ingestion(record)

            if self.api_enabled:
                try:
                    self.api.push_record(record_id, record)

                    if hasattr(self.store, "mark_readings_pushed"):
                        self.store.mark_readings_pushed([record_id])

                except KeyboardInterrupt:
                    raise
                except Exception as exc:
                    log.error(f"Push failed: {exc}")

        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.error(f"_handle_parsed failed: {exc}")

    # ----------------------------------------------------------------------
    # TESTS EXPECT run_once() TO EXIST
    # ----------------------------------------------------------------------
    def run_once(self):
        """
        Single-iteration runner used by tests and some integrations.

        Fault tolerance:
          - KeyboardInterrupt propagates
          - Any other error in read/ingest is swallowed for this iteration
        """
        try:
            raw = self.reader.read_line()
            self.process_line(raw)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.error(f"run_once failed: {exc}")
        return True

    # ----------------------------------------------------------------------
    # TESTS EXPECT run_forever() TO LOOP UNTIL KeyboardInterrupt
    # ----------------------------------------------------------------------
    def run_forever(self):
        """
        Production loop.

        Fault tolerance:
          - Loops until KeyboardInterrupt
          - Any non-KeyboardInterrupt errors in run_once() are logged and ignored
        """
        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                break
            except Exception as exc:
                # Last-ditch safety net; run_once() should already log
                log.error(f"run_forever iteration failed: {exc}")
            time.sleep(self.poll_interval)

def main():
    loop = IngestionLoop()
    loop.run_forever()

if __name__ == "__main__":
    main()

if __name__ == "app.ingestion_loop":
    main()
