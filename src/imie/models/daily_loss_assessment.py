from __future__ import annotations

import math

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DailyLossAssessment:
    broker: str
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    loss_amount: float
    maximum_daily_loss: float
    within_limit: bool
    allowed: bool
    violations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        for name in (
            "realized_pnl",
            "unrealized_pnl",
            "total_pnl",
            "loss_amount",
            "maximum_daily_loss",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            normalized = float(value)
            if not math.isfinite(normalized):
                raise ValueError(f"{name} must be finite.")
            object.__setattr__(self, name, normalized)
        if self.loss_amount < 0:
            raise ValueError("loss_amount cannot be negative.")
        if self.maximum_daily_loss <= 0:
            raise ValueError("maximum_daily_loss must be positive.")
        if not math.isclose(
            self.total_pnl,
            self.realized_pnl + self.unrealized_pnl,
            rel_tol=1e-9,
            abs_tol=1e-6,
        ):
            raise ValueError("total_pnl must equal realized plus unrealized P&L.")
        expected_loss = max(0.0, -self.total_pnl)
        if not math.isclose(
            self.loss_amount, expected_loss, rel_tol=1e-9, abs_tol=1e-6
        ):
            raise ValueError("loss_amount must match total_pnl.")
        for name in ("within_limit", "allowed"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        expected_within_limit = self.loss_amount < self.maximum_daily_loss
        if self.within_limit != expected_within_limit:
            raise ValueError("within_limit must match the daily-loss boundary.")
        if self.allowed != self.within_limit:
            raise ValueError("allowed must match within_limit.")
        if not isinstance(self.violations, tuple) or not all(
            isinstance(item, str) for item in self.violations
        ):
            raise TypeError("violations must be a tuple of strings.")
        violations = tuple(item.strip() for item in self.violations if item.strip())
        if self.allowed and violations:
            raise ValueError("allowed assessment cannot contain violations.")
        if not self.allowed and not violations:
            raise ValueError("blocked assessment requires a violation.")
        object.__setattr__(self, "broker", self.broker.strip().lower())
        object.__setattr__(self, "violations", violations)
