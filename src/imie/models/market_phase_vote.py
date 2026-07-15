from __future__ import annotations

from dataclasses import dataclass

from imie.models.market_phase_type import (
    MarketPhaseType,
)


@dataclass(frozen=True, slots=True)
class MarketPhaseVote:
    """
    Weighted support for a single market phase.
    """

    phase: MarketPhaseType

    score: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.phase,
            MarketPhaseType,
        ):
            raise TypeError(
                "phase must be a MarketPhaseType."
            )

        if self.score < 0.0:
            raise ValueError(
                "score must be greater than or equal to 0."
            )