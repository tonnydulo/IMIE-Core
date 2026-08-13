from __future__ import annotations

from dataclasses import dataclass

from imie.models.protective_coverage_status import ProtectiveCoverageStatus


@dataclass(frozen=True, slots=True)
class ProtectiveCoverageAssessment:
    broker: str | None
    symbol: str
    status: ProtectiveCoverageStatus
    position_quantity: int
    protected_quantity: int
    uncovered_quantity: int
    actionable: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.broker is not None:
            if not isinstance(self.broker, str):
                raise TypeError("broker must be a string or None.")
            broker = self.broker.strip().lower()
            if not broker:
                raise ValueError("broker cannot be empty when provided.")
            object.__setattr__(self, "broker", broker)
        if not isinstance(self.symbol, str):
            raise TypeError("symbol must be a string.")
        symbol = self.symbol.strip().upper()
        if not symbol:
            raise ValueError("symbol cannot be empty.")
        object.__setattr__(self, "symbol", symbol)
        if not isinstance(self.status, ProtectiveCoverageStatus):
            raise TypeError("status must be a ProtectiveCoverageStatus.")
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
        if not isinstance(self.actionable, bool):
            raise TypeError("actionable must be a bool.")
        for name in ("reasons", "warnings"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) for item in value
            ):
                raise TypeError(f"{name} must be a tuple of strings.")
            object.__setattr__(
                self, name, tuple(item.strip() for item in value if item.strip())
            )
        if not self.reasons:
            raise ValueError("reasons cannot be empty.")
