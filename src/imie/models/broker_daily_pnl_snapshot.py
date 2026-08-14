from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class BrokerDailyPnlSnapshot:
    """Verified broker account P&L truth for the current trading day."""

    broker: str
    realized_pnl: float
    unrealized_pnl: float
    observed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        for name in ("realized_pnl", "unrealized_pnl"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            normalized = float(value)
            if not math.isfinite(normalized):
                raise ValueError(f"{name} must be finite.")
            object.__setattr__(self, name, normalized)
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime.")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware.")
        object.__setattr__(self, "broker", self.broker.strip().lower())

    @property
    def total_pnl(self) -> float:
        return self.realized_pnl + self.unrealized_pnl

    @property
    def loss_amount(self) -> float:
        return max(0.0, -self.total_pnl)
