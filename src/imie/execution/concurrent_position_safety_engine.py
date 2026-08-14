from __future__ import annotations

from imie.models import BrokerPositionExposure, ConcurrentPositionAssessment


class ConcurrentPositionSafetyEngine:
    """Assess whether an entry would exceed verified broker exposure."""

    def assess(
        self,
        *,
        symbol: str,
        exposure: BrokerPositionExposure,
        maximum_concurrent_positions: int,
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

        normalized_symbol = symbol.strip().upper()
        symbol_already_open = exposure.contains(normalized_symbol)
        allowed = (
            symbol_already_open
            or exposure.open_position_count < maximum_concurrent_positions
        )
        violations = () if allowed else (
            "Maximum concurrent positions reached: "
            f"{exposure.open_position_count} >= {maximum_concurrent_positions}.",
        )
        return ConcurrentPositionAssessment(
            symbol=normalized_symbol,
            broker=exposure.broker,
            open_position_count=exposure.open_position_count,
            maximum_concurrent_positions=maximum_concurrent_positions,
            symbol_already_open=symbol_already_open,
            allowed=allowed,
            violations=violations,
        )
