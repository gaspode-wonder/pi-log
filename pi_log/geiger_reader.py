import argparse
import time

from pi_log.serial_reader import SerialReader
from pi_log.storage import (
    initialize_db,
    insert_reading,
    get_unpushed_readings,
    mark_readings_pushed,
)
from pi_log.push_client import PushClient


def run_pipeline(device_path, db_path, api_url, api_token, push_interval):
    initialize_db(db_path)
    client = PushClient(api_url, api_token)

    def handler(parsed):
        insert_reading(db_path, parsed)

    reader = SerialReader(device_path, handler)

    last_push = time.time()

    try:
        while True:
            # blocks until KeyboardInterrupt in tests / service stop in prod
            reader.run()

            now = time.time()
            if now - last_push >= push_interval:
                rows = get_unpushed_readings(db_path)
                pushed_ids = client.push(rows)
                if pushed_ids:
                    mark_readings_pushed(db_path, pushed_ids)
                last_push = now
    except KeyboardInterrupt:
        pass


def parse_args():
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
        required=True,
        help="LogExp ingestion API URL",
    )
    parser.add_argument(
        "--api-token",
        required=True,
        help="LogExp API token",
    )
    parser.add_argument(
        "--push-interval",
        type=int,
        default=10,
        help="Seconds between push attempts (default: 10)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(
        device_path=args.device,
        db_path=args.db,
        api_url=args.api_url,
        api_token=args.api_token,
        push_interval=args.push_interval,
    )


if __name__ == "__main__":
    main()
