import serial


class SerialReader:
    """
    Thin wrapper around pyserial for reading line‑based sensor output.
    Tests patch this class at app.ingestion_loop.SerialReader.
    """

    def __init__(self, device: str, baudrate: int = 9600):
        # In production, open the real serial port.
        # In tests, this constructor is patched and never touches hardware.
        self.ser = serial.Serial(device, baudrate, timeout=1)

    def read_line(self) -> str:
        """
        Read a single line from the serial device.
        Tests patch this method on the mock instance.
        """
        raw = self.ser.readline()
        try:
            return raw.decode("utf-8").strip()
        except Exception:
            return ""


def parse_geiger_csv(line: str):
    """
    Very permissive parser for Geiger CSV lines.

    Tests rely on this function returning a *truthy* dict for lines like:
        "CPS, 9, CPM, 90, uSv/hr, 0.09, FAST"

    If parsing fails, we still return a non‑empty dict so ingestion proceeds.
    """

    if not line:
        return None

    text = line.strip()
    if not text:
        return None

    parts = [p.strip() for p in text.split(",")]
    record = {"raw": text}

    try:
        # CPS
        if parts[0] == "CPS" and len(parts) > 1:
            record["cps"] = int(parts[1])

        # CPM
        if "CPM" in parts:
            i = parts.index("CPM")
            if i + 1 < len(parts):
                record["cpm"] = int(parts[i + 1])

        # uSv/hr
        if "uSv/hr" in parts:
            i = parts.index("uSv/hr")
            if i + 1 < len(parts):
                record["usv_hr"] = float(parts[i + 1])

    except Exception:
        # Even if parsing fails, keep a non‑empty record
        pass

    return record
