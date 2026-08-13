from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime

from imie.models.broker_order_status import (
    BrokerOrderStatus,
)


@dataclass(frozen=True, slots=True)
class BrokerOrderSnapshot:
    broker: str
    broker_order_id: str
    symbol: str
    side: str
    order_type: str
    status: BrokerOrderStatus
    requested_quantity: int
    filled_quantity: int
    remaining_quantity: int
    last_updated_at: datetime
    client_order_id: str | None = None
    average_fill_price: float | None = None
    submitted_at: datetime | None = None
    accepted_at: datetime | None = None
    filled_at: datetime | None = None
    canceled_at: datetime | None = None
    rejection_reason: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized = {}
        for name, case in (
            ("broker", "lower"),
            ("broker_order_id", None),
            ("symbol", "upper"),
            ("side", "lower"),
            ("order_type", "lower"),
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
        if not isinstance(self.status, BrokerOrderStatus):
            raise TypeError("status must be a BrokerOrderStatus.")

        for name in (
            "requested_quantity",
            "filled_quantity",
            "remaining_quantity",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")
        if self.requested_quantity <= 0:
            raise ValueError("requested_quantity must be greater than zero.")
        if self.filled_quantity + self.remaining_quantity != self.requested_quantity:
            raise ValueError(
                "filled_quantity plus remaining_quantity must equal "
                "requested_quantity."
            )

        client_order_id = self._normalize_optional_text(
            self.client_order_id,
            "client_order_id",
        )
        rejection_reason = self._normalize_optional_text(
            self.rejection_reason,
            "rejection_reason",
        )

        average_fill_price = self.average_fill_price
        if average_fill_price is not None:
            if isinstance(average_fill_price, bool) or not isinstance(
                average_fill_price,
                int | float,
            ):
                raise TypeError("average_fill_price must be a number or None.")
            average_fill_price = float(average_fill_price)
            if not math.isfinite(average_fill_price) or average_fill_price <= 0.0:
                raise ValueError(
                    "average_fill_price must be finite and greater than zero."
                )
        if self.filled_quantity == 0 and average_fill_price is not None:
            raise ValueError("average_fill_price requires a filled quantity.")
        if self.filled_quantity > 0 and average_fill_price is None:
            raise ValueError("a filled quantity requires average_fill_price.")

        for name in (
            "last_updated_at",
            "submitted_at",
            "accepted_at",
            "filled_at",
            "canceled_at",
        ):
            value = getattr(self, name)
            if value is None and name != "last_updated_at":
                continue
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime or None.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")

        if self.status is BrokerOrderStatus.FILLED:
            if self.filled_quantity != self.requested_quantity:
                raise ValueError("filled status requires the full requested quantity.")
        if self.status is BrokerOrderStatus.PARTIALLY_FILLED:
            if not 0 < self.filled_quantity < self.requested_quantity:
                raise ValueError("partially_filled status requires a partial fill.")
        if self.status is BrokerOrderStatus.REJECTED and not rejection_reason:
            raise ValueError("rejected status requires rejection_reason.")

        if not isinstance(self.warnings, tuple):
            raise TypeError("warnings must be a tuple of strings.")
        if not all(isinstance(value, str) for value in self.warnings):
            raise TypeError("warnings must be a tuple of strings.")
        warnings = tuple(value.strip() for value in self.warnings if value.strip())

        for name, value in normalized.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "client_order_id", client_order_id)
        object.__setattr__(self, "rejection_reason", rejection_reason)
        object.__setattr__(self, "average_fill_price", average_fill_price)
        object.__setattr__(self, "warnings", warnings)

    @staticmethod
    def _normalize_optional_text(value: object, name: str) -> str | None:
        if value is not None and not isinstance(value, str):
            raise TypeError(f"{name} must be a string or None.")
        return value.strip() or None if isinstance(value, str) else None

