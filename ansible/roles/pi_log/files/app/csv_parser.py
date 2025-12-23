def parse_geiger_csv(line: str):
    """
    Parse MightyOhm CSV lines of the form:
    CPS, #####, CPM, #####, uSv/hr, ###.##, MODE

    Returns a dict:
    {
        "cps": int,
        "cpm": int,
        "usv": float,
        "mode": str
    }

    Returns None for malformed or incomplete lines.
    """
    if not isinstance(line, str):
        return None

    parts = [p.strip() for p in line.split(",")]

    # Expected 7 parts:
    # ["CPS", "#####", "CPM", "#####", "uSv/hr", "###.##", "MODE"]
    if len(parts) != 7:
        return None

    try:
        cps = int(parts[1])
        cpm = int(parts[3])
        usv = float(parts[5])
        mode = parts[6]
    except (ValueError, IndexError):
        return None

    if mode not in ("SLOW", "FAST", "INST"):
        return None

    return {
        "cps": cps,
        "cpm": cpm,
        "usv": usv,
        "mode": mode,
    }
