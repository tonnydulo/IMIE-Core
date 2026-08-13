from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime

from imie.models.position_direction import PositionDirection


@dataclass(frozen=True, slots=True)
class ExecutionPosition:
    broker: str
    symbol: str
    direction: PositionDirection
    quantity: int
    average_entry_price: float | None
    market_price: float | None
    unrealized_pnl: float
    realized_pnl: float
    last_updated_at: datetime
    warnings: tuple[str, ...] = ()
    processed_fill_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(self, name, getattr(normalized, case)())

        if not isinstance(self.direction, PositionDirection):
            raise TypeError("direction must be a PositionDirection.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity < 0:
            raise ValueError("quantity cannot be negative.")

        average_entry = self._optional_positive_price(
            self.average_entry_price, "average_entry_price"
        )
        market_price = self._optional_positive_price(
            self.market_price, "market_price"
        )
        unrealized_pnl = self._finite_number(
            self.unrealized_pnl, "unrealized_pnl"
        )
        realized_pnl = self._finite_number(self.realized_pnl, "realized_pnl")

        if self.direction is PositionDirection.FLAT:
            if self.quantity != 0:
                raise ValueError("a flat position must have zero quantity.")
            if average_entry is not None:
                raise ValueError("a flat position cannot have average_entry_price.")
            if unrealized_pnl != 0.0:
                raise ValueError("a flat position must have zero unrealized_pnl.")
        else:
            if self.quantity <= 0:
                raise ValueError("a long or short position requires positive quantity.")
            if average_entry is None:
                raise ValueError(
                    "a long or short position requires average_entry_price."
                )
            if market_price is None and unrealized_pnl != 0.0:
                raise ValueError(
                    "unrealized_pnl requires market_price for an open position."
                )
            if market_price is not None:
                expected = (
                    (market_price - average_entry) * self.quantity
                    if self.direction is PositionDirection.LONG
                    else (average_entry - market_price) * self.quantity
                )
                if not math.isclose(
                    unrealized_pnl, expected, rel_tol=1e-9, abs_tol=1e-6
                ):
                    raise ValueError(
                        "unrealized_pnl does not match direction, quantity, "
                        "average entry, and market price."
                    )

        if not isinstance(self.last_updated_at, datetime):
            raise TypeError("last_updated_at must be a datetime.")
        if self.last_updated_at.tzinfo is None:
            raise ValueError("last_updated_at must be timezone-aware.")
        if not isinstance(self.warnings, tuple) or not all(
            isinstance(item, str) for item in self.warnings
        ):
            raise TypeError("warnings must be a tuple of strings.")
        if not isinstance(self.processed_fill_ids, tuple) or not all(
            isinstance(item, str) for item in self.processed_fill_ids
        ):
            raise TypeError("processed_fill_ids must be a tuple of strings.")
        processed_fill_ids = tuple(
            item.strip() for item in self.processed_fill_ids if item.strip()
        )
        if len(set(processed_fill_ids)) != len(processed_fill_ids):
            raise ValueError("processed_fill_ids cannot contain duplicates.")

        object.__setattr__(self, "average_entry_price", average_entry)
        object.__setattr__(self, "market_price", market_price)
        object.__setattr__(self, "unrealized_pnl", unrealized_pnl)
        object.__setattr__(self, "realized_pnl", realized_pnl)
        object.__setattr__(
            self,
            "warnings",
            tuple(item.strip() for item in self.warnings if item.strip()),
        )
        object.__setattr__(self, "processed_fill_ids", processed_fill_ids)

    @property
    def is_flat(self) -> bool:
        return self.direction is PositionDirection.FLAT

    @property
    def signed_quantity(self) -> int:
        if self.direction is PositionDirection.LONG:
            return self.quantity
        if self.direction is PositionDirection.SHORT:
            return -self.quantity
        return 0

    @staticmethod
    def _optional_positive_price(value: object, name: str) -> float | None:
        if value is None:
            return None
        normalized = ExecutionPosition._finite_number(value, name)
        if normalized <= 0.0:
            raise ValueError(f"{name} must be greater than zero.")
        return normalized

    @staticmethod
    def _finite_number(value: object, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise TypeError(f"{name} must be a number.")
        normalized = float(value)
        if not math.isfinite(normalized):
            raise ValueError(f"{name} must be finite.")
        return normalized
