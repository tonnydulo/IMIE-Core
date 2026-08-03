from imie.models import MarketPhaseType


def test_unknown_is_not_known() -> None:
    assert not MarketPhaseType.UNKNOWN.is_known


def test_markup_is_trending() -> None:
    assert MarketPhaseType.MARKUP.is_trending


def test_markdown_is_trending() -> None:
    assert MarketPhaseType.MARKDOWN.is_trending


def test_expansion_is_trending() -> None:
    assert MarketPhaseType.EXPANSION.is_trending


def test_reversal_identified() -> None:
    assert MarketPhaseType.REVERSAL.is_reversal


def test_transition_identified() -> None:
    assert MarketPhaseType.TRANSITION.is_transition


def test_accumulation_is_transition_phase() -> None:
    assert MarketPhaseType.ACCUMULATION.is_transition


def test_distribution_is_transition_phase() -> None:
    assert MarketPhaseType.DISTRIBUTION.is_transition