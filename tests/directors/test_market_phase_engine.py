from __future__ import annotations

import pytest

from imie.directors.market_phase_config import (
    MarketPhaseConfig,
)
from imie.directors.market_phase_engine import (
    MarketPhaseEngine,
)
from imie.directors.market_phase_resolver import (
    MarketPhaseResolver,
)
from imie.models import (
    MarketPhaseType,
)
from imie.models import (
    AnalystResult,
    MarketPhaseType,
    MarketPhaseVote,
)

def make_phase_result(
    *,
    analyst: str,
    phase: MarketPhaseType | str,
    confidence: float = 100.0,
    enabled: bool = True,
    evidence: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> AnalystResult:
    return AnalystResult(
        analyst=analyst,
        opinion="Market phase contribution.",
        confidence=confidence,
        evidence=evidence,
        warnings=warnings,
        payload={
            "market_phase": phase,
        },
        enabled=enabled,
    )

def test_default_engine_construction() -> None:
    engine = MarketPhaseEngine()

    assert isinstance(
        engine.config,
        MarketPhaseConfig,
    )

    assert isinstance(
        engine.resolver,
        MarketPhaseResolver,
    )


def test_invalid_config_raises() -> None:
    with pytest.raises(TypeError):
        MarketPhaseEngine(
            config=object(),
        )


def test_invalid_resolver_raises() -> None:
    with pytest.raises(TypeError):
        MarketPhaseEngine(
            resolver=object(),
        )


def test_default_evaluate_returns_unknown_phase() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate()

    assert result.phase is MarketPhaseType.UNKNOWN
    assert result.confidence == 0.0
    assert result.strength == 0.0
    assert result.agreement_count == 0
    assert result.conflict_count == 0
    assert len(result.unknown_domains) == 8

def test_single_structure_vote_selects_markup() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        structure=make_phase_result(
            analyst="StructureAnalyst",
            phase=MarketPhaseType.MARKUP,
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.MARKUP
    assert result.strength == 25.0
    assert result.confidence == 100.0
    assert result.agreement_count == 1
    assert result.conflict_count == 0
    assert result.supporting_domains == (
        "STRUCTURE",
    )
    assert result.opposing_domains == ()
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.MARKUP,
            score=25.0,
        ),
    )

def test_domain_confidence_scales_weighted_vote() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        auction=make_phase_result(
            analyst="AuctionAnalyst",
            phase=MarketPhaseType.ACCUMULATION,
            confidence=50.0,
        ),
    )

    assert result.phase is MarketPhaseType.ACCUMULATION
    assert result.strength == 10.0
    assert result.confidence == 100.0
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.ACCUMULATION,
            score=10.0,
        ),
    )

def test_matching_domains_combine_their_votes() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        structure=make_phase_result(
            analyst="StructureAnalyst",
            phase="MARKUP",
            confidence=100.0,
        ),
        auction=make_phase_result(
            analyst="AuctionAnalyst",
            phase="MARKUP",
            confidence=80.0,
        ),
        trend=make_phase_result(
            analyst="TrendAnalyst",
            phase="MARKUP",
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.MARKUP
    assert result.strength == 46.0
    assert result.confidence == 100.0
    assert result.agreement_count == 3
    assert result.conflict_count == 0
    assert result.supporting_domains == (
        "TREND",
        "STRUCTURE",
        "AUCTION",
    )
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.MARKUP,
            score=46.0,
        ),
    )

def test_highest_weighted_phase_wins() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        structure=make_phase_result(
            analyst="StructureAnalyst",
            phase="MARKUP",
            confidence=100.0,
        ),
        auction=make_phase_result(
            analyst="AuctionAnalyst",
            phase="PULLBACK",
            confidence=100.0,
        ),
        liquidity=make_phase_result(
            analyst="LiquidityAnalyst",
            phase="PULLBACK",
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.PULLBACK
    assert result.strength == 35.0
    assert result.confidence == 58.33
    assert result.agreement_count == 2
    assert result.conflict_count == 1
    assert result.supporting_domains == (
        "LIQUIDITY",
        "AUCTION",
    )
    assert result.opposing_domains == (
        "STRUCTURE",
    )
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.PULLBACK,
            score=35.0,
        ),
        MarketPhaseVote(
            phase=MarketPhaseType.MARKUP,
            score=25.0,
        ),
    )

def test_tied_leading_phases_resolve_transition() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        structure=make_phase_result(
            analyst="StructureAnalyst",
            phase="MARKUP",
            confidence=80.0,
        ),
        auction=make_phase_result(
            analyst="AuctionAnalyst",
            phase="MARKDOWN",
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.TRANSITION
    assert result.strength == 20.0
    assert result.confidence == 50.0
    assert result.agreement_count == 2
    assert result.conflict_count == 0
    assert result.supporting_domains == (
        "STRUCTURE",
        "AUCTION",
    )
    assert result.opposing_domains == ()
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.MARKUP,
            score=20.0,
        ),
        MarketPhaseVote(
            phase=MarketPhaseType.MARKDOWN,
            score=20.0,
        ),
    )
    assert (
        "Multiple market phases share the highest score."
        in result.warnings
    )

def test_missing_results_produce_unknown_phase() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate()

    assert result.phase is MarketPhaseType.UNKNOWN
    assert result.strength == 0.0
    assert result.confidence == 0.0
    assert result.phase_scores == ()
    assert result.agreement_count == 0
    assert result.conflict_count == 0
    assert len(
        result.unknown_domains
    ) == 8
    assert (
        "No resolved market phase votes are available."
        in result.warnings
    )

def test_disabled_result_does_not_vote() -> None:
    engine = MarketPhaseEngine()

    result = engine.evaluate(
        structure=make_phase_result(
            analyst="StructureAnalyst",
            phase="MARKUP",
            confidence=100.0,
            enabled=False,
        ),
        trend=make_phase_result(
            analyst="TrendAnalyst",
            phase="PULLBACK",
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.PULLBACK
    assert result.strength == 5.0
    assert result.confidence == 100.0
    assert result.phase_scores == (
        MarketPhaseVote(
            phase=MarketPhaseType.PULLBACK,
            score=5.0,
        ),
    )
    assert "STRUCTURE" in result.unknown_domains
    assert "TREND" in result.supporting_domains

def test_unresolved_result_does_not_vote() -> None:
    engine = MarketPhaseEngine()

    unresolved = AnalystResult(
        analyst="StructureAnalyst",
        opinion="Structure remains unclear.",
        confidence=100.0,
        evidence=(),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        structure=unresolved,
        auction=make_phase_result(
            analyst="AuctionAnalyst",
            phase="COMPRESSION",
            confidence=100.0,
        ),
    )

    assert result.phase is MarketPhaseType.COMPRESSION
    assert result.strength == 20.0
    assert result.confidence == 100.0
    assert "STRUCTURE" in result.unknown_domains
    assert "AUCTION" in result.supporting_domains

