from __future__ import annotations

import pytest

from imie.directors.institutional_confluence_engine import (
    InstitutionalConfluenceEngine,
)
from imie.models import (
    AnalystResult,
    InstitutionalConfluence,
    InstitutionalDirection,
)


def make_result(
    *,
    analyst: str,
    analyst_id: str,
    opinion: str,
    enabled: bool = True,
    confidence: float = 90.0,
    payload: object | None = None,
) -> AnalystResult:
    return AnalystResult(
        analyst=analyst,
        analyst_id=analyst_id,
        opinion=opinion,
        confidence=confidence,
        evidence=[],
        warnings=[],
        payload=payload,
        enabled=enabled,
    )


def extended_result(
    *,
    analyst: str,
    opinion: str,
    confidence: float = 90.0,
    enabled: bool = True,
) -> AnalystResult:
    return AnalystResult(
        analyst=analyst,
        opinion=opinion,
        confidence=confidence,
        evidence=[],
        warnings=[],
        enabled=enabled,
    )


def make_structure(
    opinion: str,
    *,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion=opinion,
        enabled=enabled,
    )


def make_liquidity(
    opinion: str,
    *,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=opinion,
        enabled=enabled,
    )


def make_order_block(
    opinion: str,
    *,
    enabled: bool = True,
) -> AnalystResult:
    return make_result(
        analyst="OrderBlockAnalyst",
        analyst_id="ORDER_BLOCK",
        opinion=opinion,
        enabled=enabled,
    )


def evaluate(
    *,
    structure: AnalystResult | None = None,
    liquidity: AnalystResult | None = None,
    order_block: AnalystResult | None = None,
) -> InstitutionalConfluence:
    engine = InstitutionalConfluenceEngine()

    return engine.evaluate(
        structure=structure,
        liquidity=liquidity,
        order_block=order_block,
    )


def test_returns_directional_confluence() -> None:
    result = evaluate()

    assert isinstance(
        result,
        InstitutionalConfluence,
    )

    assert result.directional_count == 3


def test_missing_results_resolve_unknown() -> None:
    result = evaluate()

    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.bullish_count == 0
    assert result.bearish_count == 0
    assert result.neutral_count == 0
    assert result.unknown_count == 3


def test_all_bullish() -> None:
    result = evaluate(
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
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )
    assert result.bullish_count == 3
    assert result.bearish_count == 0
    assert result.agreement_count == 3
    assert result.conflict_count == 0
    assert result.score == 100.0
    assert result.confidence_adjustment == 8.0


def test_all_bearish() -> None:
    result = evaluate(
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
        result.dominant_direction
        is InstitutionalDirection.BEARISH
    )
    assert result.bearish_count == 3
    assert result.bullish_count == 0
    assert result.agreement_count == 3
    assert result.conflict_count == 0
    assert result.score == 100.0
    assert result.confidence_adjustment == 8.0


def test_two_bullish_one_bearish() -> None:
    result = evaluate(
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
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )
    assert result.bullish_count == 2
    assert result.bearish_count == 1
    assert result.agreement_count == 2
    assert result.conflict_count == 1
    assert result.score == 70.0
    assert result.confidence_adjustment == 5.0


def test_two_bearish_one_bullish() -> None:
    result = evaluate(
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
        result.dominant_direction
        is InstitutionalDirection.BEARISH
    )
    assert result.bearish_count == 2
    assert result.bullish_count == 1
    assert result.agreement_count == 2
    assert result.conflict_count == 1
    assert result.score == 70.0
    assert result.confidence_adjustment == 5.0


def test_structure_and_liquidity_bullish_order_block_unknown() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active."
        ),
        order_block=make_order_block(
            "Order block context unavailable."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )
    assert result.bullish_count == 2
    assert result.unknown_count == 1
    assert result.agreement_count == 2
    assert result.conflict_count == 0
    assert result.score == 70.0


def test_liquidity_and_order_block_bearish_structure_unknown() -> None:
    result = evaluate(
        structure=make_structure(
            "Structure unavailable."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
        order_block=make_order_block(
            "Bearish order block confirmed."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.BEARISH
    )
    assert result.bearish_count == 2
    assert result.unknown_count == 1
    assert result.agreement_count == 2
    assert result.conflict_count == 0
    assert result.score == 60.0


def test_one_bullish_two_unknown() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )
    assert result.agreement_count == 1
    assert result.conflict_count == 0
    assert result.score == 40.0
    assert result.confidence_adjustment == 2.0


def test_one_bearish_two_unknown() -> None:
    result = evaluate(
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.BEARISH
    )
    assert result.agreement_count == 1
    assert result.conflict_count == 0
    assert result.score == 30.0
    assert result.confidence_adjustment == 2.0


def test_bullish_bearish_unknown_tie() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.bullish_count == 1
    assert result.bearish_count == 1
    assert result.unknown_count == 1
    assert result.agreement_count == 0
    assert result.conflict_count == 2
    assert result.score == 0.0
    assert result.confidence_adjustment == 0.0


def test_all_neutral() -> None:
    result = evaluate(
        structure=make_structure(
            "Neutral structure."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity remains balanced."
        ),
        order_block=make_order_block(
            "Institutional order flow remains balanced."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.NEUTRAL
    )
    assert result.neutral_count == 3
    assert result.agreement_count == 0
    assert result.conflict_count == 0


def test_neutral_and_unknown_resolve_unknown() -> None:
    result = evaluate(
        structure=make_structure(
            "Neutral structure."
        ),
    )

    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )
    assert result.neutral_count == 1
    assert result.unknown_count == 2


def test_disabled_results_resolve_unknown() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed.",
            enabled=False,
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active.",
            enabled=False,
        ),
        order_block=make_order_block(
            "Bullish order block confirmed.",
            enabled=False,
        ),
    )

    assert result.unknown_count == 3
    assert result.agreement_count == 0
    assert result.score == 0.0


@pytest.mark.parametrize(
    (
        "structure_opinion",
        "expected",
    ),
    [
        (
            "Bullish BOS confirmed.",
            InstitutionalDirection.BULLISH,
        ),
        (
            "Bearish CHOCH confirmed.",
            InstitutionalDirection.BEARISH,
        ),
        (
            "Neutral structure.",
            InstitutionalDirection.NEUTRAL,
        ),
        (
            "Structure unavailable.",
            InstitutionalDirection.UNKNOWN,
        ),
    ],
)
def test_structure_resolver_is_used(
    structure_opinion: str,
    expected: InstitutionalDirection,
) -> None:
    result = evaluate(
        structure=make_structure(
            structure_opinion
        ),
    )

    if expected is InstitutionalDirection.BULLISH:
        assert result.bullish_count == 1

    elif expected is InstitutionalDirection.BEARISH:
        assert result.bearish_count == 1

    elif expected is InstitutionalDirection.NEUTRAL:
        assert result.neutral_count == 1

    else:
        assert result.unknown_count == 3


@pytest.mark.parametrize(
    (
        "liquidity_opinion",
        "expected",
    ),
    [
        (
            "Demand liquidity remains active.",
            InstitutionalDirection.BULLISH,
        ),
        (
            "Supply liquidity remains active.",
            InstitutionalDirection.BEARISH,
        ),
        (
            "Liquidity remains balanced.",
            InstitutionalDirection.NEUTRAL,
        ),
        (
            "Liquidity context unavailable.",
            InstitutionalDirection.UNKNOWN,
        ),
    ],
)
def test_liquidity_resolver_is_used(
    liquidity_opinion: str,
    expected: InstitutionalDirection,
) -> None:
    result = evaluate(
        liquidity=make_liquidity(
            liquidity_opinion
        ),
    )

    if expected is InstitutionalDirection.BULLISH:
        assert result.bullish_count == 1

    elif expected is InstitutionalDirection.BEARISH:
        assert result.bearish_count == 1

    elif expected is InstitutionalDirection.NEUTRAL:
        assert result.neutral_count == 1

    else:
        assert result.unknown_count == 3


@pytest.mark.parametrize(
    (
        "order_block_opinion",
        "expected",
    ),
    [
        (
            "Bullish order block confirmed.",
            InstitutionalDirection.BULLISH,
        ),
        (
            "Bearish order block confirmed.",
            InstitutionalDirection.BEARISH,
        ),
        (
            "Institutional order flow remains balanced.",
            InstitutionalDirection.NEUTRAL,
        ),
        (
            "Order block context unavailable.",
            InstitutionalDirection.UNKNOWN,
        ),
    ],
)
def test_order_block_resolver_is_used(
    order_block_opinion: str,
    expected: InstitutionalDirection,
) -> None:
    result = evaluate(
        order_block=make_order_block(
            order_block_opinion
        ),
    )

    if expected is InstitutionalDirection.BULLISH:
        assert result.bullish_count == 1

    elif expected is InstitutionalDirection.BEARISH:
        assert result.bearish_count == 1

    elif expected is InstitutionalDirection.NEUTRAL:
        assert result.neutral_count == 1

    else:
        assert result.unknown_count == 3


def test_structure_weight_applies_when_aligned() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
    )

    assert result.structure_support is True
    assert result.score == 40.0


def test_liquidity_weight_applies_when_aligned() -> None:
    result = evaluate(
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active."
        ),
    )

    assert result.liquidity_support is True
    assert result.score == 30.0


def test_order_block_weight_applies_when_aligned() -> None:
    result = evaluate(
        order_block=make_order_block(
            "Bullish order block confirmed."
        ),
    )

    assert result.order_block_support is True
    assert result.score == 30.0


def test_conflicting_domain_does_not_add_score() -> None:
    result = evaluate(
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

    assert result.structure_support is True
    assert result.liquidity_support is False
    assert result.order_block_support is True
    assert result.score == 70.0


def test_bullish_evidence() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity demand remains active."
        ),
    )

    assert (
        "Dominant institutional direction is bullish."
        in result.evidence
    )

    assert (
        "Structure supports bullish continuation."
        in result.evidence
    )

    assert (
        "Liquidity supports bullish continuation."
        in result.evidence
    )


def test_bearish_evidence() -> None:
    result = evaluate(
        structure=make_structure(
            "Bearish structure confirmed."
        ),
        order_block=make_order_block(
            "Bearish order block confirmed."
        ),
    )

    assert (
        "Dominant institutional direction is bearish."
        in result.evidence
    )

    assert (
        "Structure supports bearish continuation."
        in result.evidence
    )

    assert (
        "Order Blocks supports bearish continuation."
        in result.evidence
    )


def test_conflict_evidence() -> None:
    result = evaluate(
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
        "Liquidity opposes bullish continuation."
        in result.evidence
    )

    assert (
        "One institutional domain conflicts with the "
        "dominant direction."
        in result.evidence
    )


def test_conflict_warning() -> None:
    result = evaluate(
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
        "Institutional disagreement detected."
        in result.warnings
    )


def test_tie_warning() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
        liquidity=make_liquidity(
            "Institutional liquidity supply remains active."
        ),
    )

    assert (
        "Bullish and bearish institutional votes are tied."
        in result.warnings
    )


def test_no_agreement_warning() -> None:
    result = evaluate()

    assert (
        "No institutional agreement detected."
        in result.warnings
    )


def test_one_agreement_warning() -> None:
    result = evaluate(
        structure=make_structure(
            "Bullish structure confirmed."
        ),
    )

    assert (
        "Only one institutional domain supports the setup."
        in result.warnings
    )


def test_full_agreement_has_no_warning() -> None:
    result = evaluate(
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

    assert result.warnings == ()


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "structure",
            object(),
        ),
        (
            "liquidity",
            "invalid",
        ),
        (
            "order_block",
            123,
        ),
    ],
)
def test_invalid_optional_results_rejected(
    field_name: str,
    value: object,
) -> None:
    values: dict[
        str,
        AnalystResult | object | None,
    ] = {
        "structure": None,
        "liquidity": None,
        "order_block": None,
    }

    values[
        field_name
    ] = value

    engine = InstitutionalConfluenceEngine()

    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} must be an "
            "AnalystResult or None"
        ),
    ):
        engine.evaluate(
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


def test_engine_is_frozen() -> None:
    engine = InstitutionalConfluenceEngine()

    with pytest.raises(
        AttributeError
    ):
        engine.structure_weight = 50.0  # type: ignore[misc]

def test_expanded_confluence_resolves_bullish() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=extended_result(
            analyst="StructureAnalyst",
            opinion="BULLISH",
        ),
        liquidity=extended_result(
            analyst="LiquidityAnalyst",
            opinion="BULLISH",
        ),
        order_block=extended_result(
            analyst="OrderBlockAnalyst",
            opinion="BULLISH",
        ),
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BULLISH",
        ),
        pressure=extended_result(
            analyst="PressureAnalyst",
            opinion="BULLISH",
        ),
        participation=extended_result(
            analyst="ParticipationAnalyst",
            opinion="BULLISH",
        ),
        value=extended_result(
            analyst="ValueAnalyst",
            opinion="BEARISH",
        ),
    )

    assert result.domain_count == 7
    assert (
        result.dominant_direction
        is InstitutionalDirection.BULLISH
    )

    assert result.bullish_count == 6
    assert result.bearish_count == 1
    assert result.neutral_count == 0
    assert result.unknown_count == 0

    assert result.agreement_count == 6
    assert result.conflict_count == 1
    assert result.score == 92.0
    assert result.confidence_adjustment == 7.0

    assert result.structure_support
    assert result.liquidity_support
    assert result.order_block_support
    assert result.auction_support
    assert result.pressure_support
    assert result.participation_support
    assert not result.value_support

def test_expanded_confluence_resolves_bearish() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=extended_result(
            analyst="StructureAnalyst",
            opinion="BEARISH",
        ),
        liquidity=extended_result(
            analyst="LiquidityAnalyst",
            opinion="BEARISH",
        ),
        order_block=extended_result(
            analyst="OrderBlockAnalyst",
            opinion="BEARISH",
        ),
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BEARISH",
        ),
        pressure=extended_result(
            analyst="PressureAnalyst",
            opinion="BEARISH",
        ),
        participation=extended_result(
            analyst="ParticipationAnalyst",
            opinion="BEARISH",
        ),
        value=extended_result(
            analyst="ValueAnalyst",
            opinion="BULLISH",
        ),
    )

    assert result.domain_count == 7
    assert (
        result.dominant_direction
        is InstitutionalDirection.BEARISH
    )

    assert result.bullish_count == 1
    assert result.bearish_count == 6
    assert result.agreement_count == 6
    assert result.conflict_count == 1
    assert result.score == 92.0
    assert result.confidence_adjustment == 7.0

def test_expanded_confluence_can_resolve_neutral() -> None:
    engine = InstitutionalConfluenceEngine()

    neutral = extended_result(
        analyst="NeutralAnalyst",
        opinion="NEUTRAL",
    )

    result = engine.evaluate(
        structure=neutral,
        liquidity=neutral,
        order_block=neutral,
        auction=neutral,
        pressure=neutral,
        participation=neutral,
        value=neutral,
    )

    assert result.domain_count == 7
    assert (
        result.dominant_direction
        is InstitutionalDirection.NEUTRAL
    )

    assert result.bullish_count == 0
    assert result.bearish_count == 0
    assert result.neutral_count == 7
    assert result.unknown_count == 0
    assert result.agreement_count == 0
    assert result.conflict_count == 0
    assert result.score == 0.0

def test_expanded_confluence_tie_resolves_unknown() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=extended_result(
            analyst="StructureAnalyst",
            opinion="BULLISH",
        ),
        liquidity=extended_result(
            analyst="LiquidityAnalyst",
            opinion="BULLISH",
        ),
        order_block=extended_result(
            analyst="OrderBlockAnalyst",
            opinion="BULLISH",
        ),
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BEARISH",
        ),
        pressure=extended_result(
            analyst="PressureAnalyst",
            opinion="BEARISH",
        ),
        participation=extended_result(
            analyst="ParticipationAnalyst",
            opinion="BEARISH",
        ),
        value=extended_result(
            analyst="ValueAnalyst",
            opinion="NEUTRAL",
        ),
    )

    assert result.domain_count == 7
    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )

    assert result.bullish_count == 3
    assert result.bearish_count == 3
    assert result.neutral_count == 1
    assert result.unknown_count == 0

    assert result.agreement_count == 0
    assert result.conflict_count == 6
    assert result.score == 0.0
    assert result.confidence_adjustment == 0.0

def test_disabled_extended_result_activates_seven_domain_mode() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=None,
        liquidity=None,
        order_block=None,
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BULLISH",
            enabled=False,
        ),
    )

    assert result.domain_count == 7
    assert (
        result.dominant_direction
        is InstitutionalDirection.UNKNOWN
    )

    assert result.unknown_count == 7
    assert result.directional_count == 7
    assert result.agreement_count == 0
    assert result.conflict_count == 0
    assert result.score == 0.0

def test_expanded_evidence_includes_all_extended_domains() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=extended_result(
            analyst="StructureAnalyst",
            opinion="BULLISH",
        ),
        liquidity=extended_result(
            analyst="LiquidityAnalyst",
            opinion="BULLISH",
        ),
        order_block=extended_result(
            analyst="OrderBlockAnalyst",
            opinion="BULLISH",
        ),
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BULLISH",
        ),
        pressure=extended_result(
            analyst="PressureAnalyst",
            opinion="BULLISH",
        ),
        participation=extended_result(
            analyst="ParticipationAnalyst",
            opinion="NEUTRAL",
        ),
        value=extended_result(
            analyst="ValueAnalyst",
            opinion="BEARISH",
        ),
    )

    assert "Auction resolves bullish." in result.evidence
    assert "Pressure resolves bullish." in result.evidence
    assert "Participation is neutral." in result.evidence
    assert "Value resolves bearish." in result.evidence

    assert (
        "Auction control supports institutional continuation."
        in result.evidence
    )

    assert (
        "Directional pressure supports institutional continuation."
        in result.evidence
    )

    assert (
        "Value opposes bullish continuation."
        in result.evidence
    )


def test_expanded_warnings_report_unresolved_and_neutral_domains() -> None:
    engine = InstitutionalConfluenceEngine()

    result = engine.evaluate(
        structure=None,
        liquidity=None,
        order_block=None,
        auction=extended_result(
            analyst="AuctionAnalyst",
            opinion="BULLISH",
        ),
        pressure=extended_result(
            analyst="PressureAnalyst",
            opinion="NEUTRAL",
        ),
        participation=None,
        value=extended_result(
            analyst="ValueAnalyst",
            opinion="BEARISH",
        ),
    )

    assert (
        "Institutional disagreement detected."
        in result.warnings
    )

    assert (
        "4 institutional domains remain unresolved."
        in result.warnings
    )

    assert (
        "1 institutional domain is neutral."
        in result.warnings
    )