# filename: app/ingestion/csv_parser.py

from __future__ import annotations

from typing import Optional, Dict, Any


def parse_geiger_csv(line: Any) -> Optional[Dict[str, Any]]:
    """
    Parse a MightyOhm-style Geiger CSV line.

    Expected format:
        CPS, <cps>, CPM, <cpm>, uSv/hr, <usv>, <mode>

    Test contract:
    - Non-string input → return None
    - Empty or whitespace-only → return None
    - Malformed or partial lines → return None
    - Valid line → return dict with keys:
        raw, cps, cpm, usv, mode
    """
    # Reject non-string input
    if not isinstance(line, str):
        return None

    raw = line.strip()
    if not raw:
        return None

    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 7:
        return None

    try:
        # Expected positions:
        # 0: "CPS"
        # 1: cps value
        # 2: "CPM"
        # 3: cpm value
        # 4: "uSv/hr"
        # 5: usv value
        # 6: mode
        cps = int(parts[1])
        cpm = int(parts[3])
        usv = float(parts[5])
        mode = parts[6]
    except Exception:
        return None

    return {
        "raw": raw,
        "cps": cps,
        "cpm": cpm,
        "usv": usv,
        "mode": mode,
    }
