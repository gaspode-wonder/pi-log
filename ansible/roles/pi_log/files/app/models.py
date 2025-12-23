from dataclasses import dataclass
from datetime import datetime


@dataclass
class GeigerRecord:
    cpm: int
    usv: float
    timestamp: datetime
