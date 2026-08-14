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
    maximum_daily_loss: float | None = None
    maximum_concurrent_positions: int | None = None
    maximum_position_exposure_age_seconds: float | None = None
    require_open_market_session: bool = False
    maximum_market_session_age_seconds: float | None = None
    kill_switch_active: bool = False
    reservation_store_path: Path = DEFAULT_EXECUTION_RESERVATION_STORE

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool.")
        if not isinstance(self.kill_switch_active, bool):
            raise TypeError("kill_switch_active must be a bool.")
        if not isinstance(self.require_open_market_session, bool):
            raise TypeError("require_open_market_session must be a bool.")
        if self.kill_switch_active and not self.enabled:
            raise ValueError(
                "kill_switch_active requires execution safety to be enabled."
            )
        if self.require_open_market_session and not self.enabled:
            raise ValueError(
                "require_open_market_session requires execution safety "
                "to be enabled."
            )
        maximum_order_notional = self._optional_positive_float(
            self.maximum_order_notional,
            "maximum_order_notional",
        )
        maximum_risk_amount = self._optional_positive_float(
            self.maximum_risk_amount,
            "maximum_risk_amount",
        )
        maximum_daily_loss = self._optional_positive_float(
            self.maximum_daily_loss,
            "maximum_daily_loss",
        )
        maximum_concurrent_positions = self._optional_positive_int(
            self.maximum_concurrent_positions,
            "maximum_concurrent_positions",
        )
        maximum_position_exposure_age_seconds = self._optional_positive_float(
            self.maximum_position_exposure_age_seconds,
            "maximum_position_exposure_age_seconds",
        )
        maximum_market_session_age_seconds = self._optional_positive_float(
            self.maximum_market_session_age_seconds,
            "maximum_market_session_age_seconds",
        )
        if maximum_concurrent_positions is not None and not self.enabled:
            raise ValueError(
                "maximum_concurrent_positions requires execution safety "
                "to be enabled."
            )
        if maximum_daily_loss is not None and not self.enabled:
            raise ValueError(
                "maximum_daily_loss requires execution safety to be enabled."
            )
        if (
            maximum_position_exposure_age_seconds is not None
            and maximum_concurrent_positions is None
        ):
            raise ValueError(
                "maximum_position_exposure_age_seconds requires "
                "maximum_concurrent_positions."
            )
        if (
            maximum_market_session_age_seconds is not None
            and not self.require_open_market_session
        ):
            raise ValueError(
                "maximum_market_session_age_seconds requires "
                "require_open_market_session."
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
        object.__setattr__(
            self,
            "maximum_position_exposure_age_seconds",
            maximum_position_exposure_age_seconds,
        )
        object.__setattr__(
            self,
            "maximum_market_session_age_seconds",
            maximum_market_session_age_seconds,
        )
        object.__setattr__(self, "maximum_risk_amount", maximum_risk_amount)
        object.__setattr__(self, "maximum_daily_loss", maximum_daily_loss)
        object.__setattr__(
            self,
            "maximum_concurrent_positions",
            maximum_concurrent_positions,
        )

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

    @staticmethod
    def _optional_positive_int(value: object, name: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an int or None.")
        if value <= 0:
            raise ValueError(f"{name} must be greater than zero.")
        return value
