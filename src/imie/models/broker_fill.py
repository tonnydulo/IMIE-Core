from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class BrokerFill:
    broker: str
    broker_order_id: str
    fill_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    executed_at: datetime

    def __post_init__(self) -> None:
        normalized = {}
        for name, case in (
            ("broker", "lower"),
            ("broker_order_id", None),
            ("fill_id", None),
            ("symbol", "upper"),
            ("side", "lower"),
        ):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            value = value.strip()
            if not value:
                raise ValueError(f"{name} cannot be empty.")
            normalized[name] = (
                value.lower()
                if case == "lower"
                else value.upper()
                if case == "upper"
                else value
            )

        if normalized["side"] not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        if isinstance(self.price, bool) or not isinstance(self.price, int | float):
            raise TypeError("price must be a number.")
        price = float(self.price)
        if not math.isfinite(price) or price <= 0.0:
            raise ValueError("price must be finite and greater than zero.")
        if not isinstance(self.executed_at, datetime):
            raise TypeError("executed_at must be a datetime.")
        if self.executed_at.tzinfo is None:
            raise ValueError("executed_at must be timezone-aware.")

        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "price", price)

