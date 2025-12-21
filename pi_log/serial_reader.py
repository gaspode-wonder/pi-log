import serial
from pi_log.csv_parser import parse_geiger_csv


class SerialReader:
    def __init__(self, device_path: str, handler):
        self.device_path = device_path
        self.handler = handler

    def run(self):
        ser = serial.Serial(self.device_path, 9600, timeout=1)

        try:
            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="ignore").strip()
                parsed = parse_geiger_csv(line)

                if parsed is not None:
                    self.handler(parsed)

        except KeyboardInterrupt:
            pass
        finally:
            ser.close()

    def run_once(self):
        ser = serial.Serial(self.device_path, 9600, timeout=1)
        try:
            raw = ser.readline()
            if not raw:
                return

            line = raw.decode("utf-8", errors="ignore").strip()
            parsed = parse_geiger_csv(line)
            if parsed is not None:
                self.handler(parsed)

        finally:
            ser.close()
