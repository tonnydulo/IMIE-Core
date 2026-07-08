from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Quote:
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: float
    volume: int = 0
    provider: str = ""

    @property
    def spread(self) -> float:
        return self.ask - self.bid
