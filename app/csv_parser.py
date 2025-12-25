def parse_geiger_csv(line: str):
    """
    Robust parser for MightyOhm Geiger CSV lines.

    Expected format:
        CPS,<cps>,CPM,<cpm>,uSv/hr,<usv>,<mode>

    Returns:
        dict with keys: cps, cpm, usv, mode, raw
        or None if the line is malformed.
    """
    if not isinstance(line, str):
        return None

    text = line.strip()
    if not text:
        return None

    parts = [p.strip() for p in text.split(",")]

    # MightyOhm always emits 7 fields when valid
    if len(parts) != 7:
        return None

    try:
        if parts[0] != "CPS":
            return None

        cps = int(parts[1])
        if parts[2] != "CPM":
            return None

        cpm = int(parts[3])
        if parts[4] != "uSv/hr":
            return None

        usv = float(parts[5])
        if usv < 0:
            return None

        mode = parts[6]
        if mode not in ("SLOW", "FAST", "INST"):
            return None

        return {
            "raw": text,
            "cps": cps,
            "cpm": cpm,
            "usv": usv,
            "mode": mode,
        }

    except Exception:
        return None
