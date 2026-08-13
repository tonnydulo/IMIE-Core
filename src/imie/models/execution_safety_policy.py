from __future__ import annotations

import math

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionSafetyPolicy:
    maximum_order_notional: float
    maximum_risk_amount: float

    def __post_init__(self) -> None:
        for name in ("maximum_order_notional", "maximum_risk_amount"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            value = float(value)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and greater than zero.")
            object.__setattr__(self, name, value)
