import json
from enum import Enum
from typing import Optional
from dataclasses import asdict, dataclass


class Unit(str, Enum):
    SECONDS = "seconds"
    MBPS = "Mbps"
    MILLISECONDS = "ms"
    PERCENT = "percent"
    DBM = "dBm"
    NONE = None

@dataclass
class PingResult:
    address: str
    success: bool
    latency: Optional[float]  # None if failed
    unit: Unit
    timestamp: str           # ISO-8601 string
    error: Optional[str] = None  # Store error message if failed

    def to_json(self):
        return json.dumps(asdict(self), default=str)
    
@dataclass
class PingTestConfig:
    host: str
    address: str
    num_pings: int
    timeout: int
    
@dataclass
class PingTestResult:
    host: str
    address: str
    unit: Unit
    average_latency: Optional[float]  # mean of successful pings
    success_rate: float               # percentage of successful pings
    timestamp: str                    # when this test finished
    metadata: Optional[PingTestConfig] = None

    def to_json(self):
        return json.dumps(asdict(self), default=str)