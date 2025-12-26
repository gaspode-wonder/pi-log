"""
Compatibility shim.

This module exists to preserve legacy import paths expected by tests.
"""

from app.serial_reader.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

__all__ = ["SerialReader", "parse_geiger_csv"]
