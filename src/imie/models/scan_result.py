from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ScanResult:
    symbol: str
    timestamp: datetime
    bias: str
    score: float
    recommendation: str
    reason: str = ""
