from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class ConcurrentPositionAssessment:
    symbol: str
    broker: str
    open_position_count: int
    maximum_concurrent_positions: int
    symbol_already_open: bool
    allowed: bool
    violations: tuple[str, ...] = ()
    exposure_age_seconds: float | None = None
    maximum_exposure_age_seconds: float | None = None
    exposure_fresh: bool = True

    def __post_init__(self) -> None:
        for name, case in (("symbol", "upper"), ("broker", "lower")):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
            object.__setattr__(self, name, getattr(value.strip(), case)())
        for name in ("open_position_count", "maximum_concurrent_positions"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
        if self.open_position_count < 0:
            raise ValueError("open_position_count cannot be negative.")
        if self.maximum_concurrent_positions <= 0:
            raise ValueError("maximum_concurrent_positions must be positive.")
        for name in ("symbol_already_open", "allowed", "exposure_fresh"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool.")
        if (self.exposure_age_seconds is None) != (
            self.maximum_exposure_age_seconds is None
        ):
            raise ValueError(
                "exposure_age_seconds and maximum_exposure_age_seconds "
                "must be provided together."
            )
        if self.exposure_age_seconds is None:
            if self.exposure_fresh is not True:
                raise ValueError("unconfigured exposure freshness must be true.")
        else:
            for name in (
                "exposure_age_seconds",
                "maximum_exposure_age_seconds",
            ):
                value = getattr(self, name)
                if isinstance(value, bool) or not isinstance(value, int | float):
                    raise TypeError(f"{name} must be a number or None.")
                normalized = float(value)
                if not math.isfinite(normalized) or normalized < 0:
                    raise ValueError(f"{name} must be finite and non-negative.")
                object.__setattr__(self, name, normalized)
            if self.maximum_exposure_age_seconds == 0:
                raise ValueError("maximum_exposure_age_seconds must be positive.")
            expected_fresh = (
                self.exposure_age_seconds
                <= self.maximum_exposure_age_seconds
            )
            if self.exposure_fresh != expected_fresh:
                raise ValueError("exposure_fresh must match the configured age.")
        expected_allowed = (
            self.exposure_fresh
            and (
                self.symbol_already_open
                or self.open_position_count < self.maximum_concurrent_positions
            )
        )
        if self.allowed != expected_allowed:
            raise ValueError("allowed must match the concurrent-position check.")
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
