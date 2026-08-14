from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math


@dataclass(frozen=True, slots=True)
class ExecutionDataFreshnessAssessment:
    checked_at: datetime
    quote_timestamp: datetime
    latest_bar_timestamp: datetime
    quote_age_seconds: float
    bar_age_seconds: float
    quote_bar_gap_seconds: float
    quote_is_fresh: bool
    bar_is_fresh: bool
    timestamps_aligned: bool
    source_actionable: bool
    allowed: bool
    status: str
    reason: str
    violations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("checked_at", "quote_timestamp", "latest_bar_timestamp"):
            value = getattr(self, name)
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")
        for name in (
            "quote_age_seconds",
            "bar_age_seconds",
            "quote_bar_gap_seconds",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise TypeError(f"{name} must be a number.")
            normalized = float(value)
            if not math.isfinite(normalized) or normalized < 0:
                raise ValueError(f"{name} must be finite and non-negative.")
            object.__setattr__(self, name, normalized)
        for name in (
            "quote_is_fresh",
            "bar_is_fresh",
            "timestamps_aligned",
            "source_actionable",
            "allowed",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        for name in ("status", "reason"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
            object.__setattr__(self, name, value.strip())
        expected_allowed = (
            self.source_actionable
            and self.quote_is_fresh
            and self.bar_is_fresh
            and self.timestamps_aligned
        )
        if self.allowed != expected_allowed:
            raise ValueError("allowed must match verified freshness truth.")
        if not isinstance(self.violations, tuple) or not all(
            isinstance(item, str) for item in self.violations
        ):
            raise TypeError("violations must be a tuple of strings.")
        violations = tuple(item.strip() for item in self.violations if item.strip())
        if self.allowed and violations:
            raise ValueError("allowed assessment cannot contain violations.")
        if not self.allowed and not violations:
            raise ValueError("blocked assessment requires a violation.")
        object.__setattr__(self, "violations", violations)
