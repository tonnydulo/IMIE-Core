from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime

from imie.models.position_direction import PositionDirection


@dataclass(frozen=True, slots=True)
class BrokerPositionSnapshot:
    broker: str
    symbol: str
    direction: PositionDirection
    quantity: int
    average_entry_price: float
    market_price: float | None
    unrealized_pnl: float
    observed_at: datetime

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(self, name, getattr(normalized, case)())
        if self.direction not in {PositionDirection.LONG, PositionDirection.SHORT}:
            raise ValueError("broker position direction must be long or short.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        for name, positive in (
            ("average_entry_price", True),
            ("market_price", True),
            ("unrealized_pnl", False),
        ):
            value = getattr(self, name)
            if value is None and name == "market_price":
                continue
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            normalized = float(value)
            if not math.isfinite(normalized):
                raise ValueError(f"{name} must be finite.")
            if positive and normalized <= 0:
                raise ValueError(f"{name} must be greater than zero.")
            object.__setattr__(self, name, normalized)
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime.")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware.")
