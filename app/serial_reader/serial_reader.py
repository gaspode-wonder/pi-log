import time
import app.serial_reader.serial as serial_shim
from app.ingestion.csv_parser import parse_geiger_csv



class SerialReader:
    """
    Reads raw lines from a serial device, parses them, and forwards parsed
    records to a callback set by the ingestion loop.

    Unit tests expect the constructor signature:
        SerialReader(device, baudrate=9600, timeout=1.0)
    """

    def __init__(self, device, baudrate=9600, timeout=1.0):
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout

        # Callback set later by ingestion loop
        self._handle_parsed = None

        # Serial comes from shim so tests can patch it
        self.ser = None

    def read_line(self):
        if self.ser is None:
            self.ser = serial_shim.Serial(
                self.device,
                self.baudrate,
                timeout=self.timeout,
            )

        raw = self.ser.readline()
        if self._handle_parsed:
            record = parse_geiger_csv(raw)
            if record is not None:
                self._handle_parsed(record)
        return raw


    def run(self):
        """
        Continuously read lines, parse them, and forward parsed records.
        Tests patch Serial.readline() to raise KeyboardInterrupt to stop the loop.
        """
        while True:
            try:
                raw = self.read_line()
                parsed = parse_geiger_csv(raw)

                if parsed is not None and self._handle_parsed:
                    self._handle_parsed(parsed)

            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(0.1)
