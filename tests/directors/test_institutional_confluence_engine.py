from __future__ import annotations

import pytest

from imie.directors.institutional_confluence_engine import (
    InstitutionalConfluenceEngine,
)
from imie.models import (
    AnalystResult,
    InstitutionalConfluence,
)


def make_result(
    *,
    analyst: str,
    analyst_id: str,
    opinion: str,
    confidence: float = 90.0,
    enabled: bool = True,
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


def make_structure(
    *,
    opinion: str = "Bullish structure confirmed.",
    enabled: bool = True,
    confidence: float = 90.0,
    payload: object | None = None,
) -> AnalystResult:
    return make_result(
        analyst="StructureAnalyst",
        analyst_id="STRUCTURE",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        payload=payload,
    )


def make_liquidity(
    *,
    opinion: str = (
        "Institutional liquidity demand remains active."
    ),
    enabled: bool = True,
    confidence: float = 90.0,
    payload: object | None = None,
) -> AnalystResult:
    return make_result(
        analyst="LiquidityAnalyst",
        analyst_id="LIQUIDITY",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        payload=payload,
    )


def make_order_block(
    *,
    opinion: str = (
        "Active institutional demand remains below price."
    ),
    enabled: bool = True,
    confidence: float = 90.0,
    payload: object | None = None,
) -> AnalystResult:
    return make_result(
        analyst="OrderBlockAnalyst",
        analyst_id="ORDER_BLOCK",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        payload=payload,
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


def test_returns_institutional_confluence() -> None:
    result = evaluate()

    assert isinstance(
        result,
        InstitutionalConfluence,
    )


def test_no_results_produces_empty_confluence() -> None:
    result = evaluate()

    assert result.score == 0.0
    assert result.agreement_count == 0
    assert result.confidence_adjustment == 0.0
    assert result.has_no_agreement is True


def test_structure_only_support() -> None:
    result = evaluate(
        structure=make_structure(),
    )

    assert result.structure_support is True
    assert result.liquidity_support is False
    assert result.order_block_support is False
    assert result.score == 40.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_liquidity_only_support() -> None:
    result = evaluate(
        liquidity=make_liquidity(),
    )

    assert result.structure_support is False
    assert result.liquidity_support is True
    assert result.order_block_support is False
    assert result.score == 30.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_order_block_only_support() -> None:
    result = evaluate(
        order_block=make_order_block(),
    )

    assert result.structure_support is False
    assert result.liquidity_support is False
    assert result.order_block_support is True
    assert result.score == 30.0
    assert result.agreement_count == 1
    assert result.confidence_adjustment == 2.0


def test_structure_and_liquidity_support() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
    )

    assert result.score == 70.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_structure_and_order_block_support() -> None:
    result = evaluate(
        structure=make_structure(),
        order_block=make_order_block(),
    )

    assert result.score == 70.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_liquidity_and_order_block_support() -> None:
    result = evaluate(
        liquidity=make_liquidity(),
        order_block=make_order_block(),
    )

    assert result.score == 60.0
    assert result.agreement_count == 2
    assert result.confidence_adjustment == 5.0


def test_full_support() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
        order_block=make_order_block(),
    )

    assert result.score == 100.0
    assert result.agreement_count == 3
    assert result.confidence_adjustment == 8.0
    assert result.has_full_agreement is True


@pytest.mark.parametrize(
    "opinion",
    [
        "Bullish structure confirmed.",
        "Bearish structure confirmed.",
        "Bullish BOS confirmed.",
        "Bearish BOS confirmed.",
        "Bullish Break of Structure confirmed.",
        "Bullish CHOCH confirmed.",
        "Bearish change of character confirmed.",
        "Bullish MSS confirmed.",
        "Bearish market structure shift confirmed.",
        "Structural confirmation is complete.",
    ],
)
def test_structure_support_opinions(
    opinion: str,
) -> None:
    result = evaluate(
        structure=make_structure(
            opinion=opinion,
        ),
    )

    assert result.structure_support is True


@pytest.mark.parametrize(
    "opinion",
    [
        "Neutral structure.",
        "No structure available.",
        "Waiting for structure.",
        "Structure is unclear.",
        "Balanced.",
    ],
)
def test_structure_unknown_opinions_do_not_support(
    opinion: str,
) -> None:
    result = evaluate(
        structure=make_structure(
            opinion=opinion,
        ),
    )

    assert result.structure_support is False


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional liquidity demand remains active.",
        "Institutional liquidity supply remains active.",
        "Institutional buy-side liquidity remains active.",
        "Institutional buy side liquidity remains active.",
        "Institutional sell-side liquidity remains active.",
        "Institutional sell side liquidity remains active.",
    ],
)
def test_liquidity_support_opinions(
    opinion: str,
) -> None:
    result = evaluate(
        liquidity=make_liquidity(
            opinion=opinion,
        ),
    )

    assert result.liquidity_support is True


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional liquidity remains balanced.",
        "No actionable institutional liquidity currently exists.",
        "Liquidity context unavailable.",
        "Waiting for liquidity.",
    ],
)
def test_liquidity_unknown_opinions_do_not_support(
    opinion: str,
) -> None:
    result = evaluate(
        liquidity=make_liquidity(
            opinion=opinion,
        ),
    )

    assert result.liquidity_support is False


@pytest.mark.parametrize(
    "opinion",
    [
        "Active institutional demand remains below price.",
        "Active institutional supply remains above price.",
        "Bullish order block confirmed.",
        "Bearish order block confirmed.",
        "Bullish block remains active.",
        "Bearish block remains active.",
    ],
)
def test_order_block_support_opinions(
    opinion: str,
) -> None:
    result = evaluate(
        order_block=make_order_block(
            opinion=opinion,
        ),
    )

    assert result.order_block_support is True


@pytest.mark.parametrize(
    "opinion",
    [
        "Institutional order flow remains balanced.",
        "No actionable institutional order blocks.",
        "Order block context unavailable.",
        "Waiting for order blocks.",
    ],
)
def test_order_block_unknown_opinions_do_not_support(
    opinion: str,
) -> None:
    result = evaluate(
        order_block=make_order_block(
            opinion=opinion,
        ),
    )

    assert result.order_block_support is False


@pytest.mark.parametrize(
    "opinion",
    [
        "bullish structure confirmed",
        "Bullish Structure Confirmed",
        "BULLISH STRUCTURE CONFIRMED",
    ],
)
def test_structure_matching_is_case_insensitive(
    opinion: str,
) -> None:
    result = evaluate(
        structure=make_structure(
            opinion=opinion,
        ),
    )

    assert result.structure_support is True


@pytest.mark.parametrize(
    "opinion",
    [
        "institutional liquidity demand remains active",
        "Institutional Liquidity Demand Remains Active",
        "INSTITUTIONAL LIQUIDITY DEMAND REMAINS ACTIVE",
    ],
)
def test_liquidity_matching_is_case_insensitive(
    opinion: str,
) -> None:
    result = evaluate(
        liquidity=make_liquidity(
            opinion=opinion,
        ),
    )

    assert result.liquidity_support is True


@pytest.mark.parametrize(
    "opinion",
    [
        "bullish order block confirmed",
        "Bullish Order Block Confirmed",
        "BULLISH ORDER BLOCK CONFIRMED",
    ],
)
def test_order_block_matching_is_case_insensitive(
    opinion: str,
) -> None:
    result = evaluate(
        order_block=make_order_block(
            opinion=opinion,
        ),
    )

    assert result.order_block_support is True


def test_disabled_structure_is_ignored() -> None:
    result = evaluate(
        structure=make_structure(
            enabled=False,
        ),
    )

    assert result.structure_support is False
    assert result.score == 0.0


def test_disabled_liquidity_is_ignored() -> None:
    result = evaluate(
        liquidity=make_liquidity(
            enabled=False,
        ),
    )

    assert result.liquidity_support is False
    assert result.score == 0.0


def test_disabled_order_block_is_ignored() -> None:
    result = evaluate(
        order_block=make_order_block(
            enabled=False,
        ),
    )

    assert result.order_block_support is False
    assert result.score == 0.0


def test_disabled_results_do_not_count_as_agreement() -> None:
    result = evaluate(
        structure=make_structure(
            enabled=False,
        ),
        liquidity=make_liquidity(
            enabled=False,
        ),
        order_block=make_order_block(
            enabled=False,
        ),
    )

    assert result.agreement_count == 0
    assert result.confidence_adjustment == 0.0


def test_confidence_values_do_not_change_support() -> None:
    result = evaluate(
        structure=make_structure(
            confidence=0.0,
        ),
        liquidity=make_liquidity(
            confidence=1.0,
        ),
        order_block=make_order_block(
            confidence=100.0,
        ),
    )

    assert result.agreement_count == 3
    assert result.score == 100.0


def test_payloads_do_not_change_support() -> None:
    result = evaluate(
        structure=make_structure(
            payload=object(),
        ),
        liquidity=make_liquidity(
            payload=object(),
        ),
        order_block=make_order_block(
            payload=object(),
        ),
    )

    assert result.agreement_count == 3
    assert result.score == 100.0


def test_structure_evidence_is_included() -> None:
    result = evaluate(
        structure=make_structure(),
    )

    assert (
        "Structure confirms institutional continuation."
        in result.evidence
    )


def test_liquidity_evidence_is_included() -> None:
    result = evaluate(
        liquidity=make_liquidity(),
    )

    assert (
        "Liquidity supports institutional continuation."
        in result.evidence
    )


def test_order_block_evidence_is_included() -> None:
    result = evaluate(
        order_block=make_order_block(),
    )

    assert (
        "Order Blocks support institutional continuation."
        in result.evidence
    )


def test_one_domain_agreement_evidence() -> None:
    result = evaluate(
        structure=make_structure(),
    )

    assert (
        "One institutional domain supports the setup."
        in result.evidence
    )


def test_two_domain_agreement_evidence() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
    )

    assert (
        "Two institutional domains support the setup."
        in result.evidence
    )


def test_three_domain_agreement_evidence() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
        order_block=make_order_block(),
    )

    assert (
        "Three institutional domains support the setup."
        in result.evidence
    )


def test_no_agreement_warning() -> None:
    result = evaluate()

    assert result.warnings == (
        "No institutional agreement detected.",
    )


def test_one_agreement_warning() -> None:
    result = evaluate(
        structure=make_structure(),
    )

    assert result.warnings == (
        "Only one institutional domain supports the setup.",
    )


def test_two_agreements_have_no_warning() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
    )

    assert result.warnings == ()


def test_three_agreements_have_no_warning() -> None:
    result = evaluate(
        structure=make_structure(),
        liquidity=make_liquidity(),
        order_block=make_order_block(),
    )

    assert result.warnings == ()


def test_missing_results_are_ignored() -> None:
    result = evaluate(
        structure=None,
        liquidity=make_liquidity(),
        order_block=None,
    )

    assert result.structure_support is False
    assert result.liquidity_support is True
    assert result.order_block_support is False


def test_supporting_domains_are_correct() -> None:
    result = evaluate(
        structure=make_structure(),
        order_block=make_order_block(),
    )

    assert result.supporting_domains == (
        "STRUCTURE",
        "ORDER_BLOCK",
    )


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
def test_invalid_optional_result_is_rejected(
    field_name: str,
    value: object,
) -> None:
    arguments: dict[str, object | None] = {
        "structure": None,
        "liquidity": None,
        "order_block": None,
    }

    arguments[
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
            structure=arguments[
                "structure"
            ],  # type: ignore[arg-type]
            liquidity=arguments[
                "liquidity"
            ],  # type: ignore[arg-type]
            order_block=arguments[
                "order_block"
            ],  # type: ignore[arg-type]
        )


def test_default_weights() -> None:
    engine = InstitutionalConfluenceEngine()

    assert engine.structure_weight == 40.0
    assert engine.liquidity_weight == 30.0
    assert engine.order_block_weight == 30.0


@pytest.mark.parametrize(
    (
        "structure_weight",
        "liquidity_weight",
        "order_block_weight",
    ),
    [
        (
            -1.0,
            50.0,
            51.0,
        ),
        (
            40.0,
            -1.0,
            61.0,
        ),
        (
            40.0,
            61.0,
            -1.0,
        ),
    ],
)
def test_negative_weight_is_rejected(
    structure_weight: float,
    liquidity_weight: float,
    order_block_weight: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        InstitutionalConfluenceEngine(
            structure_weight=structure_weight,
            liquidity_weight=liquidity_weight,
            order_block_weight=order_block_weight,
        )


@pytest.mark.parametrize(
    (
        "structure_weight",
        "liquidity_weight",
        "order_block_weight",
    ),
    [
        (
            40.0,
            30.0,
            20.0,
        ),
        (
            50.0,
            30.0,
            30.0,
        ),
    ],
)
def test_weights_must_total_one_hundred(
    structure_weight: float,
    liquidity_weight: float,
    order_block_weight: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Institutional confluence weights "
            "must total 100"
        ),
    ):
        InstitutionalConfluenceEngine(
            structure_weight=structure_weight,
            liquidity_weight=liquidity_weight,
            order_block_weight=order_block_weight,
        )