# filename: app/ingestion/geiger_reader.py

import argparse
import logging
import sys

from app.ingestion.api_client import PushClient
from app.ingestion.serial_reader import SerialReader
from app.ingestion.watchdog import WatchdogSerialReader

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geiger_reader",
        description="Ingestion loop for MightyOhm Geiger counter readings.",
    )

    parser.add_argument("--device", required=True, type=str)
    parser.add_argument("--baudrate", required=True, type=int)
    parser.add_argument("--device-type", required=True, choices=["mightyohm"])
    parser.add_argument("--db", required=True, type=str)
    parser.add_argument("--api-url", required=True, type=str)
    parser.add_argument("--api-token", required=False, default="", type=str)
    parser.add_argument("--device-id", required=True, type=str)

    return parser


def main() -> int:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logging.info("Starting ingestion agent")
    logging.info(f"Device: {args.device}")
    logging.info(f"Baudrate: {args.baudrate}")
    logging.info(f"Device type: {args.device_type}")
    logging.info(f"DB path: {args.db}")
    logging.info(f"API URL: {args.api_url}")
    logging.info(
        "API token: <empty>" if args.api_token == "" else "API token: <provided>"
    )
    logging.info(f"Device ID: {args.device_id}")

    base_reader = SerialReader(
        device=args.device,
        baudrate=args.baudrate,
    )

    reader = WatchdogSerialReader(base_reader)


    client = PushClient(
        api_url=args.api_url,
        api_token=args.api_token,
        device_id=args.device_id,
        db_path=args.db,
    )

    reader.set_handler(client.handle_record)
    reader.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
