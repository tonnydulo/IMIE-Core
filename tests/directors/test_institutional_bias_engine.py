from __future__ import annotations

import pytest

from imie.directors.institutional_bias_config import (
    InstitutionalBiasConfig,
)
from imie.directors.institutional_bias_engine import (
    InstitutionalBiasEngine,
)
from imie.models import (
    AnalystResult,
    InstitutionalBias,
    InstitutionalDirection,
)


def make_result(
    *,
    analyst: str,
    analyst_id: str,
    opinion: str,
    confidence: float = 80.0,
    enabled: bool = True,
    evidence: list[str] | None = None,
    warnings: list[str] | None = None,
    payload: object | None = None,
) -> AnalystResult:
    return AnalystResult(
        analyst=analyst,
        analyst_id=analyst_id,
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        evidence=evidence or [],
        warnings=warnings or [],
        payload=payload,
    )


def make_trend(
    opinion: str,
    *,
    confidence: float = 80.0,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
    )


def make_structure(
    opinion: str,
    *,
    confidence: float = 80.0,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
    )


def make_liquidity(
    opinion: str,
    *,
    confidence: float = 80.0,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
    )


def make_order_block(
    opinion: str,
    *,
    confidence: float = 80.0,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="OrderBlockAnalyst",
        analyst_id="ORDER_BLOCK",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
    )


def evaluate(
    *,
    trend: AnalystResult | None = None,
    structure: AnalystResult | None = None,
    liquidity: AnalystResult | None = None,
    order_block: AnalystResult | None = None,
    config: InstitutionalBiasConfig | None = None,
) -> InstitutionalBias:
    engine = InstitutionalBiasEngine(
        config=(
            config
            or InstitutionalBiasConfig()
        )
    )

    return engine.evaluate(
        trend=trend,
        structure=structure,
        liquidity=liquidity,
        order_block=order_block,
    )


def test_returns_institutional_bias() -> None:
    result = evaluate()

    assert isinstance(
        result,
        InstitutionalBias,
    )


def test_missing_results_produce_unknown_bias() -> None:
    result = evaluate()

    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.bullish_score == 0.0
    assert result.bearish_score == 0.0
    assert result.confidence == 0.0
    assert result.agreement_count == 0
    assert result.conflict_count == 0


def test_all_core_domains_are_classified() -> None:
    result = evaluate()

    assert result.unknown_domains == (
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    )


def test_all_bullish_core_domains() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active."
        ),
        order_block=make_order_block(
            "Bullish order block confirmed."
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.bullish_score == 60.0
    assert result.bearish_score == 0.0
    assert result.strength == 60.0
    assert result.confidence == 80.0
    assert result.agreement_count == 4
    assert result.conflict_count == 0

    assert result.supporting_domains == (
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
    )


def test_all_bearish_core_domains() -> None:
    result = evaluate(
        trend=make_trend(
            "Bearish trend confirmed."
        ),
        structure=make_structure(
            "Bearish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
        order_block=make_order_block(
            "Bearish order block confirmed."
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BEARISH
    )
    assert result.bullish_score == 0.0
    assert result.bearish_score == 60.0
    assert result.strength == 60.0
    assert result.confidence == 80.0
    assert result.agreement_count == 4
    assert result.conflict_count == 0


def test_default_core_weight_is_seventy_five() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=100.0,
        ),
        structure=make_structure(
            "Bullish structure confirmed.",
            confidence=100.0,
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active.",
            confidence=100.0,
        ),
        order_block=make_order_block(
            "Bullish order block confirmed.",
            confidence=100.0,
        ),
    )

    assert result.bullish_score == 75.0


def test_trend_weighted_score() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=80.0,
        ),
    )

    assert result.bullish_score == 20.0
    assert result.bearish_score == 0.0


def test_structure_weighted_score() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed.",
            confidence=80.0,
        ),
    )

    assert result.bullish_score == 16.0


def test_liquidity_weighted_score() -> None:
    result = evaluate(
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active.",
            confidence=80.0,
        ),
    )

    assert result.bullish_score == 12.0


def test_order_block_weighted_score() -> None:
    result = evaluate(
        order_block=make_order_block(
            "Bullish order block confirmed.",
            confidence=80.0,
        ),
    )

    assert result.bullish_score == 12.0


def test_bullish_majority_with_bearish_conflict() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
        order_block=make_order_block(
            "Bullish order block confirmed."
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )
    assert result.bullish_score == 48.0
    assert result.bearish_score == 12.0
    assert result.strength == 36.0
    assert result.agreement_count == 3
    assert result.conflict_count == 1
    assert result.confidence == 60.0

    assert result.opposing_domains == (
        "LIQUIDITY",
    )


def test_bearish_majority_with_bullish_conflict() -> None:
    result = evaluate(
        trend=make_trend(
            "Bearish trend confirmed."
        ),
        structure=make_structure(
            "Bearish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active."
        ),
        order_block=make_order_block(
            "Bearish order block confirmed."
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.BEARISH
    )
    assert result.bullish_score == 12.0
    assert result.bearish_score == 48.0
    assert result.agreement_count == 3
    assert result.conflict_count == 1


def test_weighted_direction_can_differ_from_domain_count() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=100.0,
        ),
        structure=make_structure(
            "Bearish structure confirmed.",
            confidence=40.0,
        ),
        liquidity=make_liquidity(
            "Bearish liquidity supply remains active.",
            confidence=40.0,
        ),
    )

    assert result.bullish_score == 25.0
    assert result.bearish_score == 14.0

    assert (
        result.direction
        is InstitutionalDirection.BULLISH
    )

    assert result.agreement_count == 1
    assert result.conflict_count == 2


def test_exact_score_tie_produces_neutral_bias() -> None:
    config = InstitutionalBiasConfig(
        trend_weight=25.0,
        structure_weight=25.0,
        liquidity_weight=15.0,
        order_block_weight=10.0,
        auction_weight=10.0,
        pressure_weight=5.0,
        participation_weight=5.0,
        value_weight=5.0,
    )

    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=80.0,
        ),
        structure=make_structure(
            "Bearish structure confirmed.",
            confidence=80.0,
        ),
        config=config,
    )

    assert result.bullish_score == 20.0
    assert result.bearish_score == 20.0
    assert result.strength == 0.0

    assert (
        result.direction
        is InstitutionalDirection.NEUTRAL
    )

    assert result.agreement_count == 0
    assert result.conflict_count == 0

    assert result.neutral_domains == (
        "TREND",
        "STRUCTURE",
    )


def test_neutral_domain_contributes_zero() -> None:
    result = evaluate(
        trend=make_trend(
            "Neutral trend."
        ),
    )

    assert result.bullish_score == 0.0
    assert result.bearish_score == 0.0
    assert result.neutral_domains == (
        "TREND",
    )


def test_unknown_domain_contributes_zero() -> None:
    result = evaluate(
        trend=make_trend(
            "Trend context unavailable."
        ),
    )

    assert result.bullish_score == 0.0
    assert result.bearish_score == 0.0

    assert "TREND" in result.unknown_domains


def test_disabled_domain_contributes_zero() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            enabled=False,
        ),
    )

    assert result.bullish_score == 0.0
    assert result.bearish_score == 0.0

    assert "TREND" in result.unknown_domains


def test_zero_confidence_directional_domain_contributes_zero() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=0.0,
        ),
    )

    assert (
        result.direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.bullish_score == 0.0
    assert result.confidence == 0.0


def test_single_directional_domain_confidence() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=80.0,
        ),
    )

    assert result.confidence == 80.0
    assert result.agreement_count == 1
    assert result.conflict_count == 0


def test_conflict_reduces_confidence() -> None:
    aligned = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bullish structure confirmed."
        ),
    )

    conflicted = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bearish structure confirmed."
        ),
    )

    assert aligned.confidence == 80.0
    assert conflicted.confidence < aligned.confidence


def test_low_spread_reduces_confidence() -> None:
    config = InstitutionalBiasConfig(
        minimum_directional_spread=10.0,
    )

    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=40.0,
        ),
        structure=make_structure(
            "Bearish structure confirmed.",
            confidence=40.0,
        ),
        liquidity=make_liquidity(
            "Bullish liquidity demand remains active.",
            confidence=40.0,
        ),
        config=config,
    )

    assert result.strength < 10.0

    assert (
        "Institutional score spread is below the configured "
        "directional quality threshold."
        in result.warnings
    )


def test_low_confidence_warning() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=20.0,
        ),
    )

    assert result.confidence == 20.0

    assert (
        "Institutional bias confidence is below the configured "
        "minimum."
        in result.warnings
    )


def test_conflict_warning() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bearish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Bullish liquidity demand remains active."
        ),
    )

    assert (
        "Institutional domains conflict with the dominant bias."
        in result.warnings
    )


def test_unknown_bias_warning() -> None:
    result = evaluate()

    assert (
        "No directional institutional bias is available."
        in result.warnings
    )


def test_neutral_bias_warning() -> None:
    config = InstitutionalBiasConfig(
        trend_weight=25.0,
        structure_weight=25.0,
        liquidity_weight=15.0,
        order_block_weight=10.0,
        auction_weight=10.0,
        pressure_weight=5.0,
        participation_weight=5.0,
        value_weight=5.0,
    )

    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
        structure=make_structure(
            "Bearish structure confirmed."
        ),
        config=config,
    )

    assert (
        "Bullish and bearish institutional scores are tied."
        in result.warnings
    )


def test_extended_domains_are_unresolved() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
    )

    for domain in (
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    ):
        assert domain in result.unknown_domains


def test_extended_domains_do_not_affect_scores() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=100.0,
        ),
    )

    assert result.bullish_score == 25.0
    assert result.bearish_score == 0.0


def test_evidence_reports_bias_direction() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed."
        ),
    )

    assert (
        "Dominant institutional bias is bullish."
        in result.evidence
    )


def test_evidence_reports_scores() -> None:
    result = evaluate(
        trend=make_trend(
            "Bullish trend confirmed.",
            confidence=80.0,
        ),
    )

    assert (
        "Bullish institutional score is 20.00."
        in result.evidence
    )

    assert (
        "Bearish institutional score is 0.00."
        in result.evidence
    )


def test_result_evidence_is_preserved() -> None:
    trend = make_result(
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion="Bullish trend confirmed.",
        confidence=80.0,
        evidence=[
            "Price is above EMA9.",
        ],
    )

    result = evaluate(
        trend=trend
    )

    assert (
        "Price is above EMA9."
        in result.evidence
    )


def test_result_warnings_are_preserved() -> None:
    trend = make_result(
        analyst="TrendAnalyst",
        analyst_id="TREND",
        opinion="Bullish trend confirmed.",
        confidence=80.0,
        warnings=[
            "Trend is losing momentum.",
        ],
    )

    result = evaluate(
        trend=trend
    )

    assert (
        "Trend is losing momentum."
        in result.warnings
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "trend",
            object(),
        ),
        (
            "structure",
            "invalid",
        ),
        (
            "liquidity",
            123,
        ),
        (
            "order_block",
            [],
        ),
    ],
)
def test_invalid_optional_results_are_rejected(
    field_name: str,
    value: object,
) -> None:
    values: dict[str, object | None] = {
        "trend": None,
        "structure": None,
        "liquidity": None,
        "order_block": None,
    }

    values[
        field_name
    ] = value

    engine = InstitutionalBiasEngine()

    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be an "
            "AnalystResult or None"
        ),
    ):
        engine.evaluate(
            trend=values[
                "trend"
            ],  # type: ignore[arg-type]
            structure=values[
                "structure"
            ],  # type: ignore[arg-type]
            liquidity=values[
                "liquidity"
            ],  # type: ignore[arg-type]
            order_block=values[
                "order_block"
            ],  # type: ignore[arg-type]
        )


def test_engine_rejects_invalid_config() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "config must be an InstitutionalBiasConfig"
        ),
    ):
        InstitutionalBiasEngine(
            config=object(),  # type: ignore[arg-type]
        )


def test_engine_is_frozen() -> None:
    engine = InstitutionalBiasEngine()

    with pytest.raises(
        AttributeError
    ):
        engine.config = (  # type: ignore[misc]
            InstitutionalBiasConfig()
        )

def test_auction_contributes_to_bullish_bias() -> None:
    engine = InstitutionalBiasEngine()

    auction = AnalystResult(
        analyst="AuctionAnalyst",
        opinion="Buyers control the auction.",
        confidence=80.0,
        evidence=("Auction acceptance favors buyers.",),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        trend=None,
        structure=None,
        liquidity=None,
        order_block=None,
        auction=auction,
    )

    assert result.direction is InstitutionalDirection.BULLISH
    assert result.bullish_score == 8.0
    assert result.bearish_score == 0.0
    assert "AUCTION" in result.supporting_domains
    assert "AUCTION" not in result.unknown_domains

def test_pressure_contributes_to_bearish_bias() -> None:
    engine = InstitutionalBiasEngine()

    pressure = AnalystResult(
        analyst="PressureAnalyst",
        opinion="Buying pressure exhausted.",
        confidence=60.0,
        evidence=("Buying pressure is weakening.",),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        trend=None,
        structure=None,
        liquidity=None,
        order_block=None,
        pressure=pressure,
    )

    assert result.direction is InstitutionalDirection.BEARISH
    assert result.bullish_score == 0.0
    assert result.bearish_score == 3.0
    assert "PRESSURE" in result.supporting_domains

def test_participation_contributes_to_bullish_bias() -> None:
    engine = InstitutionalBiasEngine()

    participation = AnalystResult(
        analyst="ParticipationAnalyst",
        opinion="Strong bullish participation.",
        confidence=100.0,
        evidence=("Buyers are participating aggressively.",),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        trend=None,
        structure=None,
        liquidity=None,
        order_block=None,
        participation=participation,
    )

    assert result.direction is InstitutionalDirection.BULLISH
    assert result.bullish_score == 5.0
    assert "PARTICIPATION" in result.supporting_domains

def test_value_contributes_to_bearish_bias() -> None:
    engine = InstitutionalBiasEngine()

    value = AnalystResult(
        analyst="ValueAnalyst",
        opinion="Price is rejecting above value.",
        confidence=80.0,
        evidence=("Price is trading above accepted value.",),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        trend=None,
        structure=None,
        liquidity=None,
        order_block=None,
        value=value,
    )

    assert result.direction is InstitutionalDirection.BEARISH
    assert result.bearish_score == 4.0
    assert "VALUE" in result.supporting_domains

def test_all_eight_domains_participate_in_bias() -> None:
    engine = InstitutionalBiasEngine()

    bullish = AnalystResult(
        analyst="CoreAnalyst",
        opinion="BULLISH",
        confidence=100.0,
        evidence=(),
        warnings=(),
        payload={},
        enabled=True,
    )

    result = engine.evaluate(
        trend=bullish,
        structure=bullish,
        liquidity=bullish,
        order_block=bullish,
        auction=AnalystResult(
            analyst="AuctionAnalyst",
            opinion="Buyers control the auction.",
            confidence=100.0,
            evidence=(),
            warnings=(),
            payload={},
            enabled=True,
        ),
        pressure=AnalystResult(
            analyst="PressureAnalyst",
            opinion="Selling pressure exhausted.",
            confidence=100.0,
            evidence=(),
            warnings=(),
            payload={},
            enabled=True,
        ),
        participation=AnalystResult(
            analyst="ParticipationAnalyst",
            opinion="Bullish participation expanding.",
            confidence=100.0,
            evidence=(),
            warnings=(),
            payload={},
            enabled=True,
        ),
        value=AnalystResult(
            analyst="ValueAnalyst",
            opinion="BULLISH",
            confidence=100.0,
            evidence=(),
            warnings=(),
            payload={},
            enabled=True,
        ),
    )

    assert result.direction is InstitutionalDirection.BULLISH
    assert result.bullish_score == 100.0
    assert result.bearish_score == 0.0
    assert result.strength == 100.0
    assert result.agreement_count == 8
    assert result.conflict_count == 0
    assert result.supporting_domains == (
        "TREND",
        "STRUCTURE",
        "LIQUIDITY",
        "ORDER_BLOCK",
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    )
    assert result.opposing_domains == ()
    assert result.neutral_domains == ()
    assert result.unknown_domains == ()
    assert result.confidence == 100.0

