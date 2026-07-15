from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    MarketPhase,
    MarketPhaseType,
    MarketPhaseVote,
)


def test_market_phase_is_immutable() -> None:
    phase = MarketPhase(
        phase=MarketPhaseType.MARKUP,
        confidence=85.0,
        strength=80.0,
        phase_scores=(),
        agreement_count=6,
        conflict_count=1,
        supporting_domains=("STRUCTURE",),
        opposing_domains=(),
        neutral_domains=(),
        unknown_domains=(),
        evidence=("Markup confirmed.",),
        warnings=(),
    )

    with pytest.raises(FrozenInstanceError):
        phase.confidence = 10.0


def test_market_phase_fields() -> None:
    phase = MarketPhase(
        phase=MarketPhaseType.EXPANSION,
        confidence=90.0,
        strength=88.0,
        phase_scores=(),
        agreement_count=7,
        conflict_count=0,
        supporting_domains=("TREND", "STRUCTURE"),
        opposing_domains=(),
        neutral_domains=(),
        unknown_domains=(),
        evidence=("Expansion confirmed.",),
        warnings=(),
    )

    assert phase.phase is MarketPhaseType.EXPANSION
    assert phase.confidence == 90.0
    assert phase.strength == 88.0
    assert phase.agreement_count == 7
    assert phase.conflict_count == 0

def test_market_phase_stores_phase_scores() -> None:
    phase = MarketPhase(
        phase=MarketPhaseType.MARKUP,
        confidence=90.0,
        strength=75.0,
        phase_scores=(
            MarketPhaseVote(
                phase=MarketPhaseType.MARKUP,
                score=75.0,
            ),
            MarketPhaseVote(
                phase=MarketPhaseType.PULLBACK,
                score=20.0,
            ),
        ),
        agreement_count=5,
        conflict_count=1,
        supporting_domains=("STRUCTURE",),
        opposing_domains=("LIQUIDITY",),
        neutral_domains=(),
        unknown_domains=(),
        evidence=(),
        warnings=(),
    )

    assert phase.phase_scores == (
    MarketPhaseVote(
        phase=MarketPhaseType.MARKUP,
        score=75.0,
    ),
    MarketPhaseVote(
        phase=MarketPhaseType.PULLBACK,
        score=20.0,
    ),
)