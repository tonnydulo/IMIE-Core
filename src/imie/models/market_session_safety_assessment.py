from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MarketSessionSafetyAssessment:
    broker: str
    session_open: bool
    observed_at: datetime
    next_open: datetime | None
    next_close: datetime | None
    allowed: bool
    violations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str) or not self.broker.strip():
            raise ValueError("broker must be a non-empty string.")
        for name in ("session_open", "allowed"):
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
        if self.allowed != self.session_open:
            raise ValueError("allowed must match session_open.")
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
