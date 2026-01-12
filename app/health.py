# filename: app/health.py

from __future__ import annotations
from typing import Dict


def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint for tests and monitoring.
    Returns a dict with a static OK status.
    """
    return {"status": "ok"}
