from xml.sax import handler
import serial
from app.csv_parser import parse_geiger_csv


class SerialReader:
    def __init__(self, device, baudrate, handler=None):
        self.device = device
        self.baudrate = baudrate
        self.handler = handler or (lambda line: None)

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
