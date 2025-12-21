import time
from app.serial_reader import SerialReader
from app.csv_parser import parse_geiger_csv
from app.sqlite_store import SQLiteStore
from app.api_client import APIClient
from app.config import settings
from app.logging_loader import get_logger
log = get_logger(__name__)


class IngestionLoop:
    """
    Orchestrates the full ingestion pipeline:
      - Read raw lines from serial
      - Parse CSV into structured data
      - Store in SQLite
      - Optionally push to remote API
    """

    def __init__(self):
        self.reader = SerialReader(
            device=settings.serial["device"],
            baudrate=settings.serial["baudrate"],
        )
        self.store = SQLiteStore(settings.sqlite["path"])

        self.api_enabled = settings.api["enabled"]
        if self.api_enabled:
            self.api = APIClient(
                base_url=settings.api["base_url"],
                token=settings.api["token"],
            )

        self.poll_interval = settings.ingestion["poll_interval"]

    def process_line(self, raw_line: str):
        """Parse, store, and optionally push a single line."""
        parsed = parse_geiger_csv(raw_line)
        record_id = self.store.insert_record(parsed)

        log.debug(f"Stored record {record_id}: {parsed}")

        if self.api_enabled:
            self.api.push_record(record_id, parsed)

    def run_forever(self):
        log.info("Starting ingestion loop")

        while True:
            try:
                raw = self.reader.read_line()
                if raw:
                    self.process_line(raw)
            except Exception as exc:
                log.exception(f"Ingestion error: {exc}")

            time.sleep(self.poll_interval)

