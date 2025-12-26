"""
Compatibility shim for tests.

We expose ONLY:
    parse_geiger_csv

We intentionally do NOT import or re-export Serial here.
Tests patch:
    app.serial_reader.serial.Serial
and SerialReader imports from that module directly.
"""

from app.ingestion.csv_parser import parse_geiger_csv

__all__ = ["parse_geiger_csv"]
