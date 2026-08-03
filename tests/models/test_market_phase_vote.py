from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    MarketPhaseType,
    MarketPhaseVote,
)


def test_vote_is_immutable() -> None:
    vote = MarketPhaseVote(
        phase=MarketPhaseType.MARKUP,
        score=25.0,
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        vote.score = 10.0


def test_negative_score_raises() -> None:
    with pytest.raises(
        ValueError,
    ):
        MarketPhaseVote(
            phase=MarketPhaseType.MARKUP,
            score=-1.0,
        )


def test_invalid_phase_raises() -> None:
    with pytest.raises(
        TypeError,
    ):
        MarketPhaseVote(
            phase="MARKUP",
            score=10.0,
        )


def test_vote_fields() -> None:
    vote = MarketPhaseVote(
        phase=MarketPhaseType.EXPANSION,
        score=42.5,
    )

    assert vote.phase is MarketPhaseType.EXPANSION
    assert vote.score == 42.5