from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math


@dataclass(frozen=True, slots=True)
class MarketSessionSafetyAssessment:
    broker: str
    session_open: bool
    observed_at: datetime
    next_open: datetime | None
    next_close: datetime | None
    allowed: bool
    violations: tuple[str, ...] = ()
    session_age_seconds: float | None = None
    maximum_session_age_seconds: float | None = None
    session_fresh: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        for name in ("session_open", "allowed", "session_fresh"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        for name in ("observed_at", "next_open", "next_close"):
            value = getattr(self, name)
            if value is None and name != "observed_at":
                continue
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime or None.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")
        if (self.session_age_seconds is None) != (
            self.maximum_session_age_seconds is None
        ):
            raise ValueError(
                "session_age_seconds and maximum_session_age_seconds "
                "must be provided together."
            )
        if self.session_age_seconds is None:
            if self.session_fresh is not True:
                raise ValueError("unconfigured session freshness must be true.")
        else:
            for name in (
                "session_age_seconds",
                "maximum_session_age_seconds",
            ):
                value = getattr(self, name)
                if isinstance(value, bool) or not isinstance(value, int | float):
                    raise TypeError(f"{name} must be a number or None.")
                normalized = float(value)
                if not math.isfinite(normalized) or normalized < 0:
                    raise ValueError(f"{name} must be finite and non-negative.")
                object.__setattr__(self, name, normalized)
            if self.maximum_session_age_seconds == 0:
                raise ValueError("maximum_session_age_seconds must be positive.")
            expected_fresh = (
                self.session_age_seconds <= self.maximum_session_age_seconds
            )
            if self.session_fresh != expected_fresh:
                raise ValueError("session_fresh must match the configured age.")
        if self.allowed != (self.session_open and self.session_fresh):
            raise ValueError(
                "allowed must match session_open and session_fresh."
            )
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
