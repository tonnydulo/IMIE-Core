from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.protected_order_slice import ProtectedOrderSlice


@dataclass(frozen=True, slots=True)
class ExistingPositionProtectionPlan:
    broker: str
    symbol: str
    position_side: str
    exit_side: str
    position_quantity: int
    protected_quantity: int
    uncovered_quantity: int
    time_in_force: str
    position_updated_at: datetime
    slices: tuple[ProtectedOrderSlice, ...]
    valid: bool
    actionable: bool
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            value = value.strip()
            if not value:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(self, name, getattr(value, case)())
        for name in ("position_side", "exit_side"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            value = value.strip().lower()
            if value not in {"buy", "sell"}:
                raise ValueError(f"{name} must be buy or sell.")
            object.__setattr__(self, name, value)
        if self.position_side == self.exit_side:
            raise ValueError("exit_side must oppose position_side.")
        for name in (
            "position_quantity",
            "protected_quantity",
            "uncovered_quantity",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")
        if self.protected_quantity + self.uncovered_quantity != self.position_quantity:
            raise ValueError(
                "protected and uncovered quantities must equal position quantity."
            )
        if not isinstance(self.slices, tuple) or not all(
            isinstance(item, ProtectedOrderSlice) for item in self.slices
        ):
            raise TypeError("slices must be a tuple of ProtectedOrderSlice.")
        if sum(item.quantity for item in self.slices) != self.uncovered_quantity:
            raise ValueError("slice quantities must equal uncovered_quantity.")
        labels = tuple(item.label for item in self.slices)
        if labels not in {("target1",), ("target1", "target2")}:
            raise ValueError("slices must be ordered as target1, target2.")
        if len({item.stop_price for item in self.slices}) != 1:
            raise ValueError("all slices must use the same stop price.")
        if not isinstance(self.time_in_force, str):
            raise TypeError("time_in_force must be a string.")
        time_in_force = self.time_in_force.strip().lower()
        if time_in_force not in {"day", "gtc"}:
            raise ValueError("time_in_force must be day or gtc.")
        object.__setattr__(self, "time_in_force", time_in_force)
        if not isinstance(self.position_updated_at, datetime):
            raise TypeError("position_updated_at must be a datetime.")
        if self.position_updated_at.tzinfo is None:
            raise ValueError("position_updated_at must be timezone-aware.")
        for name in ("valid", "actionable"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        if not self.valid or not self.actionable:
            raise ValueError("an existing-position protection plan must be actionable.")
        for name in ("reasons", "warnings"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) for item in value
            ):
                raise TypeError(f"{name} must be a tuple of strings.")
            object.__setattr__(
                self, name, tuple(item.strip() for item in value if item.strip())
            )

    @property
    def stop_price(self) -> float:
        return self.slices[0].stop_price
