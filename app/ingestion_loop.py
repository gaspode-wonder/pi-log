"""
Compatibility shim for legacy imports and test patch paths.

Historically, ingestion lived in `app.ingestion_loop`.
After refactoring, the implementation moved to `app.ingestion.ingestion_loop`.

This module re-exports the key symbols so that existing imports,
tests, and systemd units that reference `app.ingestion_loop`
continue to work without modification.
"""

from app.ingestion.ingestion_loop import (
    IngestionLoop,
    build_ingestion_loop,
    get_settings,
    main,
    SQLiteStore,
)

# Re-export the real SerialReader and parser
from app.ingestion.serial_reader import SerialReader
from app.ingestion.csv_parser import parse_geiger_csv

# Re-export API clients
from app.api_client import APIClient
from app.logexp_client import LogExpClient

# Re-export metrics module so tests can patch metrics.record_ingestion
import app.metrics as metrics

__all__ = [
    "IngestionLoop",
    "build_ingestion_loop",
    "get_settings",
    "main",
    "SQLiteStore",
    "SerialReader",
    "parse_geiger_csv",
    "APIClient",
    "LogExpClient",
    "metrics",
]
