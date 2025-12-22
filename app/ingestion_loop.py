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
    Ingestion loop:
      - Reads lines until KeyboardInterrupt
      - Parses each line
      - Stores valid records
      - Records metrics
      - Optionally pushes to API
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

    def process_line(self, raw):
        """
        Parse, store, record metrics, and optionally push a single raw line.
        Returns True if processed, False if malformed.
        """
        record = parse_geiger_csv(raw)
        if not record:
            return False

        # Store record
        record_id = self.store.insert_record(record)

        # Metrics hook (tests patch app.metrics.record_ingestion)
        metrics.record_ingestion(record)

        # Optional API push
        if self.api_enabled:
            try:
                self.api.push_record(record_id, record)

                # Only call if the store actually implements it
                if hasattr(self.store, "mark_readings_pushed"):
                    self.store.mark_readings_pushed([record_id])

            except Exception as exc:
                log.error(f"Push failed: {exc}")

        return True

    def run_once(self):
        """
        Execute a single ingestion iteration.
        Raises KeyboardInterrupt when reader does.
        """
        raw = self.reader.read_line()  # may raise KeyboardInterrupt
        self.process_line(raw)
        return True

    def run_forever(self):
        """
        Production loop. Tests expect:
          - Loop until KeyboardInterrupt
          - Do not swallow KeyboardInterrupt
        """
        while True:
            self.run_once()
            time.sleep(self.poll_interval)
