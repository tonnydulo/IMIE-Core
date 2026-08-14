from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class BrokerMarketSessionSnapshot:
    """Read-only broker truth about the current market session."""

    broker: str
    is_open: bool
    observed_at: datetime
    next_open: datetime | None = None
    next_close: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        if not isinstance(self.is_open, bool):
            raise TypeError("is_open must be a bool.")
        for name in ("observed_at", "next_open", "next_close"):
            value = getattr(self, name)
            if value is None and name != "observed_at":
                continue
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime or None.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")
        object.__setattr__(self, "broker", self.broker.strip().lower())
