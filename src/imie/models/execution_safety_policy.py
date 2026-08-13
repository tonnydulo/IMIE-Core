from __future__ import annotations

import math

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionSafetyPolicy:
    maximum_order_notional: float
    maximum_risk_amount: float
    kill_switch_active: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.kill_switch_active, bool):
            raise TypeError("kill_switch_active must be a bool.")
        for name in ("maximum_order_notional", "maximum_risk_amount"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            value = float(value)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and greater than zero.")
            object.__setattr__(self, name, value)
