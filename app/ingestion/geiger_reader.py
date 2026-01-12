# filename: app/ingestion/geiger_reader.py

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from typing import Any

from app.serial_reader import SerialReader
from app.sqlite_store import (
    initialize_db,
    insert_record,
    get_unpushed_records,
    mark_records_pushed,
)
from app.api_client import PushClient
from app.models import GeigerRecord


def run_pipeline(
    device_path: str,
    db_path: str,
    api_url: str | None,
    api_token: str | None,
    push_interval: int,
    device_id: str = "pi-log",
) -> None:
    """
    Main ingestion pipeline for Pi-log.

    Responsibilities:
        - Initialize SQLite DB
        - Continuously read MightyOhm CSV lines
        - Parse them into canonical GeigerRecord objects
        - Store them locally (including raw + timestamp)
        - Periodically push unpushed records to LogExp (if enabled)
        - Mark records as pushed on success
    """

    initialize_db(db_path)

    # API push is optional now
    push_enabled = bool(api_url and api_token)
    client = PushClient(api_url, api_token) if push_enabled else None

    def handle_parsed(parsed: dict[str, Any]) -> None:
        """
        Convert parsed CSV dict → GeigerRecord → SQLite row.
        """
        record = GeigerRecord.from_parsed(
            parsed,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
        )
        insert_record(db_path, record)

    reader = SerialReader(device_path)
    reader._handle_parsed = handle_parsed

    last_push = time.time()

    try:
        while True:
            # Blocks until KeyboardInterrupt in tests or service stop in prod
            reader.run()

            now = time.time()
            if now - last_push >= push_interval:
                if push_enabled:
                    assert client is not None  # type narrowing for Pylance

                    records = get_unpushed_records(db_path)
                    if records:
                        pushed_ids = client.push(records)
                        if pushed_ids:
                            mark_records_pushed(db_path, pushed_ids)

                last_push = now


    except KeyboardInterrupt:
        # Graceful shutdown for tests and service stop
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pi-Log Geiger counter ingestion service"
    )

    parser.add_argument(
        "--device",
        default="/dev/ttyUSB0",
        help="Serial device path (default: /dev/ttyUSB0)",
    )
    parser.add_argument(
        "--db",
        default="/var/lib/pi-log/readings.db",
        help="SQLite DB path (default: /var/lib/pi-log/readings.db)",
    )
    parser.add_argument(
        "--api-url",
        required=False,
        help="LogExp ingestion API URL",
    )
    parser.add_argument(
        "--api-token",
        required=False,
        help="LogExp API token",
    )
    parser.add_argument(
        "--push-interval",
        type=int,
        default=10,
        help="Seconds between push attempts (default: 10)",
    )
    parser.add_argument(
        "--device-id",
        default="pi-log",
        help="Logical device identifier sent to LogExp (default: pi-log)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(
        device_path=args.device,
        db_path=args.db,
        api_url=args.api_url,
        api_token=args.api_token,
        push_interval=args.push_interval,
        device_id=args.device_id,
    )


if __name__ == "__main__":
    main()
