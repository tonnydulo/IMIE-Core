from __future__ import annotations

import math

from dataclasses import dataclass

from imie.models.broker_order_status import BrokerOrderStatus


@dataclass(frozen=True, slots=True)
class ExecutionReconciliationResult:
    broker: str
    broker_order_id: str
    symbol: str
    side: str
    status: BrokerOrderStatus
    intent_quantity: int
    broker_requested_quantity: int
    broker_filled_quantity: int
    recorded_fill_quantity: int
    broker_average_fill_price: float | None
    recorded_average_fill_price: float | None
    identity_matched: bool
    quantity_matched: bool
    fills_matched: bool
    reconciled: bool
    discrepancies: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("broker", "broker_order_id", "symbol", "side"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(
                self,
                name,
                normalized.upper() if name == "symbol" else normalized.lower()
                if name in {"broker", "side"}
                else normalized,
            )
        if self.side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell.")
        if not isinstance(self.status, BrokerOrderStatus):
            raise TypeError("status must be a BrokerOrderStatus.")

        for name in (
            "intent_quantity",
            "broker_requested_quantity",
            "broker_filled_quantity",
            "recorded_fill_quantity",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")

        for name in (
            "broker_average_fill_price",
            "recorded_average_fill_price",
        ):
            value = getattr(self, name)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number or None.")
            normalized = float(value)
            if not math.isfinite(normalized) or normalized <= 0.0:
                raise ValueError(f"{name} must be finite and positive.")
            object.__setattr__(self, name, normalized)

        for name in (
            "identity_matched",
            "quantity_matched",
            "fills_matched",
            "reconciled",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")

        discrepancies = self._normalize_messages(
            self.discrepancies,
            "discrepancies",
        )
        warnings = self._normalize_messages(self.warnings, "warnings")
        if self.reconciled and discrepancies:
            raise ValueError("a reconciled result cannot have discrepancies.")
        if self.reconciled and not (
            self.identity_matched and self.quantity_matched and self.fills_matched
        ):
            raise ValueError("a reconciled result requires every comparison to match.")
        if not self.reconciled and not discrepancies:
            raise ValueError("an unreconciled result requires discrepancies.")
        object.__setattr__(self, "discrepancies", discrepancies)
        object.__setattr__(self, "warnings", warnings)

    @staticmethod
    def _normalize_messages(value: object, name: str) -> tuple[str, ...]:
        if not isinstance(value, tuple) or not all(
            isinstance(item, str) for item in value
        ):
            raise TypeError(f"{name} must be a tuple of strings.")
        return tuple(item.strip() for item in value if item.strip())

