"""
Compatibility shim for tests.

This package exposes:
    - SerialReader (forwarded from serial_reader.py)
    - parse_geiger_csv (forwarded from csv_parser)

It intentionally does NOT re-export Serial.
Tests patch:
    app.serial_reader.serial.Serial
and SerialReader imports from that module directly.
"""

from .serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

__all__ = ["SerialReader", "parse_geiger_csv"]
