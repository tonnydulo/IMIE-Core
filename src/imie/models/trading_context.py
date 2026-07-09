from dataclasses import dataclass

from imie.models.market_measurements import MarketMeasurements
from imie.models.market_observations import MarketObservations
from imie.models.market_snapshot import MarketSnapshot


@dataclass(frozen=True)
class TradingContext:
    snapshot: MarketSnapshot
    measurements: MarketMeasurements
    observations: MarketObservations
