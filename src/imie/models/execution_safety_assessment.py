from __future__ import annotations

import math

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionSafetyAssessment:
    symbol: str
    order_notional: float
    risk_amount: float
    maximum_order_notional: float
    maximum_risk_amount: float
    candidate_valid: bool
    candidate_actionable: bool
    notional_within_limit: bool
    risk_within_limit: bool
    allowed: bool
    kill_switch_active: bool = False
    violations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        object.__setattr__(self, "symbol", self.symbol.strip().upper())
        for name in (
            "order_notional",
            "risk_amount",
            "maximum_order_notional",
            "maximum_risk_amount",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            value = float(value)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative.")
            object.__setattr__(self, name, value)
        for name in (
            "notional_within_limit",
            "risk_within_limit",
            "candidate_valid",
            "candidate_actionable",
            "allowed",
            "kill_switch_active",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        if self.allowed != (
            self.notional_within_limit
            and self.risk_within_limit
            and self.candidate_valid
            and self.candidate_actionable
            and not self.kill_switch_active
        ):
            raise ValueError("allowed must match the individual safety checks.")
        for name in ("violations", "warnings"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(item, str) for item in value
            ):
                raise TypeError(f"{name} must be a tuple of strings.")
            object.__setattr__(
                self, name, tuple(item.strip() for item in value if item.strip())
            )
        if self.allowed and self.violations:
            raise ValueError("allowed assessment cannot contain violations.")
        if not self.allowed and not self.violations:
            raise ValueError("blocked assessment requires at least one violation.")
