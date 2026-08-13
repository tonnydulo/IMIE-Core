from __future__ import annotations

import math

from dataclasses import dataclass
from pathlib import Path

from imie.models import ExecutionSafetyPolicy


DEFAULT_EXECUTION_RESERVATION_STORE = Path(
    "runtime/execution/submission_reservations.json"
)


@dataclass(frozen=True, slots=True)
class ExecutionSafetyConfig:
    """Explicit runtime configuration for guarded broker submission."""

    enabled: bool = False
    maximum_order_notional: float | None = None
    maximum_risk_amount: float | None = None
    kill_switch_active: bool = False
    reservation_store_path: Path = DEFAULT_EXECUTION_RESERVATION_STORE

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool.")
        if not isinstance(self.kill_switch_active, bool):
            raise TypeError("kill_switch_active must be a bool.")
        if self.kill_switch_active and not self.enabled:
            raise ValueError(
                "kill_switch_active requires execution safety to be enabled."
            )
        maximum_order_notional = self._optional_positive_float(
            self.maximum_order_notional,
            "maximum_order_notional",
        )
        maximum_risk_amount = self._optional_positive_float(
            self.maximum_risk_amount,
            "maximum_risk_amount",
        )
        if not isinstance(self.reservation_store_path, Path):
            raise TypeError("reservation_store_path must be a Path.")
        if not str(self.reservation_store_path).strip():
            raise ValueError("reservation_store_path cannot be empty.")
        if self.enabled and maximum_order_notional is None:
            raise ValueError(
                "maximum_order_notional is required when execution safety "
                "is enabled."
            )
        if self.enabled and maximum_risk_amount is None:
            raise ValueError(
                "maximum_risk_amount is required when execution safety is enabled."
            )
        object.__setattr__(
            self, "maximum_order_notional", maximum_order_notional
        )
        object.__setattr__(self, "maximum_risk_amount", maximum_risk_amount)

    def build_policy(self) -> ExecutionSafetyPolicy:
        if not self.enabled:
            raise RuntimeError(
                "execution safety must be enabled before building a policy."
            )
        assert self.maximum_order_notional is not None
        assert self.maximum_risk_amount is not None
        return ExecutionSafetyPolicy(
            maximum_order_notional=self.maximum_order_notional,
            maximum_risk_amount=self.maximum_risk_amount,
            kill_switch_active=self.kill_switch_active,
        )

    @staticmethod
    def _optional_positive_float(value: object, name: str) -> float | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise TypeError(f"{name} must be numeric or None.")
        normalized = float(value)
        if not math.isfinite(normalized) or normalized <= 0:
            raise ValueError(f"{name} must be finite and greater than zero.")
        return normalized
