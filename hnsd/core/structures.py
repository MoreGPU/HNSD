from enum import Enum
from dataclasses import dataclass

from typing import Optional

@dataclass
class IPAddress:
    value: str

class Unit(str, Enum):
    SECONDS = "seconds"
    MBPS = "Mbps"
    MILLISECONDS = "ms"
    PERCENT = "percent"
    DBM = "dBm"
    NONE = None

@dataclass
class Metric:
    value: float
    unit: Optional[Unit] = None
    
@dataclass
class SpeedTestResult:
    download: Metric
    upload: Metric
    ping: Metric
    
@dataclass
class WifiTestResult:
    rssi: Metric
    noise: Metric
    snr: Metric
    channel: Metric
    
@dataclass
class PingTestResult:
    ping: Metric