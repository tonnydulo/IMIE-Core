from __future__ import annotations

from imie.models import BrokerPositionExposure, ConcurrentPositionAssessment
from datetime import datetime
import math


class ConcurrentPositionSafetyEngine:
    """Assess whether an entry would exceed verified broker exposure."""

    def assess(
        self,
        *,
        symbol: str,
        exposure: BrokerPositionExposure,
        maximum_concurrent_positions: int,
        checked_at: datetime | None = None,
        maximum_exposure_age_seconds: float | None = None,
    ) -> ConcurrentPositionAssessment:
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        if not isinstance(exposure, BrokerPositionExposure):
            raise TypeError("exposure must be a BrokerPositionExposure.")
        if (
            isinstance(maximum_concurrent_positions, bool)
            or not isinstance(maximum_concurrent_positions, int)
        ):
            raise TypeError("maximum_concurrent_positions must be an int.")
        if maximum_concurrent_positions <= 0:
            raise ValueError("maximum_concurrent_positions must be positive.")
        if (checked_at is None) != (maximum_exposure_age_seconds is None):
            raise ValueError(
                "checked_at and maximum_exposure_age_seconds must be "
                "configured together."
            )

        exposure_age_seconds = None
        exposure_fresh = True
        if checked_at is not None:
            if not isinstance(checked_at, datetime):
                raise TypeError("checked_at must be a datetime or None.")
            if checked_at.tzinfo is None:
                raise ValueError("checked_at must be timezone-aware.")
            if (
                isinstance(maximum_exposure_age_seconds, bool)
                or not isinstance(maximum_exposure_age_seconds, int | float)
            ):
                raise TypeError(
                    "maximum_exposure_age_seconds must be a number or None."
                )
            maximum_exposure_age_seconds = float(
                maximum_exposure_age_seconds
            )
            if (
                not math.isfinite(maximum_exposure_age_seconds)
                or maximum_exposure_age_seconds <= 0
            ):
                raise ValueError(
                    "maximum_exposure_age_seconds must be finite and positive."
                )
            exposure_age_seconds = (
                checked_at - exposure.observed_at
            ).total_seconds()
            if exposure_age_seconds < 0:
                raise ValueError("broker exposure cannot be observed in the future.")
            exposure_fresh = (
                exposure_age_seconds <= maximum_exposure_age_seconds
            )

        normalized_symbol = symbol.strip().upper()
        symbol_already_open = exposure.contains(normalized_symbol)
        position_limit_allowed = (
            symbol_already_open
            or exposure.open_position_count < maximum_concurrent_positions
        )
        violations = []
        if not exposure_fresh:
            violations.append(
                "Broker position exposure is stale: "
                f"{exposure_age_seconds:.3f}s > "
                f"{maximum_exposure_age_seconds:.3f}s."
            )
        if not position_limit_allowed:
            violations.append(
                "Maximum concurrent positions reached: "
                f"{exposure.open_position_count} >= "
                f"{maximum_concurrent_positions}."
            )
        allowed = exposure_fresh and position_limit_allowed
        return ConcurrentPositionAssessment(
            symbol=normalized_symbol,
            broker=exposure.broker,
            open_position_count=exposure.open_position_count,
            maximum_concurrent_positions=maximum_concurrent_positions,
            symbol_already_open=symbol_already_open,
            allowed=allowed,
            violations=tuple(violations),
            exposure_age_seconds=exposure_age_seconds,
            maximum_exposure_age_seconds=maximum_exposure_age_seconds,
            exposure_fresh=exposure_fresh,
        )
