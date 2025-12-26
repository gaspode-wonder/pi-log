"""
Shim exposing Serial for tests.

Tests patch:
    @patch("app.serial_reader.serial.Serial")

This avoids conflicts with the real 'serial' package.
"""

import serial as _serial

Serial = _serial.Serial

__all__ = ["Serial"]
