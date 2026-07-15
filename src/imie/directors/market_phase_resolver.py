from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    MarketPhaseType,
)


@dataclass(frozen=True, slots=True)
class MarketPhaseResolver:
    """
    Resolves a normalized MarketPhaseType from an AnalystResult.
    """

    def resolve(
        self,
        result: AnalystResult | None,
    ) -> MarketPhaseType:

        if result is None:
            return MarketPhaseType.UNKNOWN

        if not result.enabled:
            return MarketPhaseType.UNKNOWN

        payload = result.payload

        if not isinstance(payload, dict):
            return MarketPhaseType.UNKNOWN

        phase = payload.get("market_phase")

        if isinstance(
            phase,
            MarketPhaseType,
        ):
            return phase

        if isinstance(
            phase,
            str,
        ):
            try:
                return MarketPhaseType[
                    phase.strip().upper()
                ]

            except KeyError:
                return MarketPhaseType.UNKNOWN

        return MarketPhaseType.UNKNOWN