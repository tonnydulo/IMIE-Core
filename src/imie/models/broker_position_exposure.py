from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class BrokerPositionExposure:
    """Verified broker-wide open-position symbols at one observation time."""

    broker: str
    open_symbols: tuple[str, ...]
    observed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        if not isinstance(self.open_symbols, tuple) or not all(
            isinstance(symbol, str) for symbol in self.open_symbols
        ):
            raise TypeError("open_symbols must be a tuple of strings.")
        symbols = tuple(symbol.strip().upper() for symbol in self.open_symbols)
        if any(not symbol for symbol in symbols):
            raise ValueError("open_symbols cannot contain empty symbols.")
        if len(set(symbols)) != len(symbols):
            raise ValueError("open_symbols cannot contain duplicates.")
        if not isinstance(self.observed_at, datetime):
            raise TypeError("observed_at must be a datetime.")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware.")
        object.__setattr__(self, "broker", self.broker.strip().lower())
        object.__setattr__(self, "open_symbols", tuple(sorted(symbols)))

    @property
    def open_position_count(self) -> int:
        return len(self.open_symbols)

    def contains(self, symbol: str) -> bool:
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        return symbol.strip().upper() in self.open_symbols
