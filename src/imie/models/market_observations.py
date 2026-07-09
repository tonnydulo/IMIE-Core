from dataclasses import dataclass


@dataclass(frozen=True)
class MarketObservations:
    price_above_ema9: bool = False
    price_below_ema9: bool = False
    price_above_vwap: bool = False
    price_below_vwap: bool = False
    ema9_rising: bool = False
    ema9_falling: bool = False
    within_core_zone: bool = False
    approaching_core: bool = False
