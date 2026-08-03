from dataclasses import dataclass, field
from datetime import datetime

from imie.models.market_bar import MarketBar
from imie.models.quote import Quote


@dataclass(frozen=True)
class MarketFacts:
    ema9: float | None = None
    vwap: float | None = None
    atr14: float | None = None
    rvol: float | None = None


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    timestamp: datetime
    quote: Quote
    bars: list[MarketBar]
    timeframe: str
    facts: MarketFacts = field(default_factory=MarketFacts)
