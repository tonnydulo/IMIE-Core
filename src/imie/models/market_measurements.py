from dataclasses import dataclass


@dataclass(frozen=True)
class MarketMeasurements:
    price: float
    ema9: float | None = None
    previous_ema9: float | None = None
    ema9_slope: float | None = None
    vwap: float | None = None
    atr14: float | None = None
    nearest_core: str = "none"
    nearest_core_price: float | None = None
    distance_to_core: float | None = None
    atr_distance_to_core: float | None = None
    core_tolerance: float | None = None
