# filename: app/serial_reader/__init__.py
"""
Serial reader package.

This package exposes:
    - SerialReader (from serial_reader.py)
    - parse_geiger_csv (from app.ingestion.csv_parser)

SerialReader now uses the real pyserial.Serial class directly.
Tests patch serial.Serial to simulate device behavior.
"""

from .serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

__all__ = ["SerialReader", "parse_geiger_csv"]
