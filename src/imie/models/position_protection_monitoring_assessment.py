from __future__ import annotations

import math

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PositionProtectionMonitoringAssessment:
    broker: str
    symbol: str
    state: str
    checked_at: datetime
    observed_at: datetime | None
    observation_age_seconds: float | None
    maximum_age_seconds: float
    reconciliation_state: str | None
    healthy: bool
    action_required: bool
    reason: str
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
            object.__setattr__(self, name, getattr(value.strip(), case)())
        if self.state not in {
            "never_observed",
            "fresh_healthy",
            "fresh_unhealthy",
            "stale",
        }:
            raise ValueError("state is not a supported monitoring state.")
        if not isinstance(self.checked_at, datetime) or self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be a timezone-aware datetime.")
        if self.observed_at is not None and (
            not isinstance(self.observed_at, datetime)
            or self.observed_at.tzinfo is None
        ):
            raise ValueError("observed_at must be timezone-aware or None.")
        for name in ("observation_age_seconds", "maximum_age_seconds"):
            value = getattr(self, name)
            if value is None and name == "observation_age_seconds":
                continue
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            if not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"{name} must be finite and non-negative.")
            object.__setattr__(self, name, float(value))
        if not isinstance(self.healthy, bool) or not isinstance(
            self.action_required, bool
        ):
            raise TypeError("healthy and action_required must be bools.")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")
        object.__setattr__(self, "reason", self.reason.strip())
        if not isinstance(self.warnings, tuple) or not all(
            isinstance(item, str) for item in self.warnings
        ):
            raise TypeError("warnings must be a tuple of strings.")
        object.__setattr__(
            self,
            "warnings",
            tuple(item.strip() for item in self.warnings if item.strip()),
        )
