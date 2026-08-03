from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketBar:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    timeframe: str
    provider: str = ""

    @property
    def range(self) -> float:
        return self.high - self.low
