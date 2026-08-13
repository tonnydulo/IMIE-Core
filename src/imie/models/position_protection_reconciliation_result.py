from __future__ import annotations

from dataclasses import dataclass

from imie.models.broker_order_snapshot import BrokerOrderSnapshot


@dataclass(frozen=True, slots=True)
class PositionProtectionReconciliationResult:
    broker: str
    symbol: str
    state: str
    requested_quantity: int
    active_quantity: int
    triggered_quantity: int
    reconciled: bool
    snapshots: tuple[BrokerOrderSnapshot, ...]
    discrepancies: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
            object.__setattr__(self, name, getattr(value.strip(), case)())
        if self.state not in {
            "active",
            "triggered",
            "degraded",
            "terminal_unprotected",
            "indeterminate",
        }:
            raise ValueError("state is not a supported reconciliation state.")
        for name in ("requested_quantity", "active_quantity", "triggered_quantity"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")
        if self.active_quantity > self.requested_quantity:
            raise ValueError("active_quantity cannot exceed requested_quantity.")
        if self.triggered_quantity > self.requested_quantity:
            raise ValueError("triggered_quantity cannot exceed requested_quantity.")
        if not isinstance(self.reconciled, bool):
            raise TypeError("reconciled must be a bool.")
        if not isinstance(self.snapshots, tuple) or not all(
            isinstance(item, BrokerOrderSnapshot) for item in self.snapshots
        ):
            raise TypeError("snapshots must be a tuple of BrokerOrderSnapshot.")
        for name in ("discrepancies", "warnings"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) for item in value
            ):
                raise TypeError(f"{name} must be a tuple of strings.")
            object.__setattr__(
                self, name, tuple(item.strip() for item in value if item.strip())
            )
