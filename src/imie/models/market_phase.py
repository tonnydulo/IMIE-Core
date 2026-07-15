from __future__ import annotations

from dataclasses import dataclass

from imie.models.market_phase_type import (
    MarketPhaseType,
)
from imie.models.market_phase_vote import (
    MarketPhaseVote,
)


@dataclass(frozen=True, slots=True)
class MarketPhase:
    """
    Immutable institutional market phase assessment.

    This model represents the current stage of the institutional
    auction independently from directional bias.
    """

    phase: MarketPhaseType

    confidence: float

    strength: float

    phase_scores: tuple[
        MarketPhaseVote,
        ...,
    ]

    agreement_count: int

    conflict_count: int

    supporting_domains: tuple[str, ...]

    opposing_domains: tuple[str, ...]

    neutral_domains: tuple[str, ...]

    unknown_domains: tuple[str, ...]

    evidence: tuple[str, ...]

    warnings: tuple[str, ...]