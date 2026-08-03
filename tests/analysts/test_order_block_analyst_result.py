from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.analysts import OrderBlockAnalyst
from imie.models import (
    AnalystResult,
    OrderBlockAnalysis,
    OrderBlockFinding,
    OrderBlockLifecycleState,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockStateType,
)


def make_finding(
    *,
    side: OrderBlockSide = OrderBlockSide.BULLISH,
    confidence: float = 92.0,
) -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=550.00,
        lower=549.50,
        side=side,
        origin=OrderBlockOrigin.BOS,
        source_bar_index=10,
        displacement=0.50,
        strength=88.0,
        confidence=confidence,
        reason="Institutional order block.",
        evidence=(
            "Order block confirmed.",
        ),
        detector="OrderBlockBuilder",
    )


def make_state(
    *,
    side: OrderBlockSide = OrderBlockSide.BULLISH,
    state: OrderBlockStateType = OrderBlockStateType.ACTIVE,
) -> OrderBlockLifecycleState:
    touch_count = 0
    mitigation_count = 0
    last_touch_bar: int | None = None

    if state is OrderBlockStateType.TESTED:
        touch_count = 1
        last_touch_bar = 15

    elif state is OrderBlockStateType.MITIGATED:
        touch_count = 1
        mitigation_count = 1
        last_touch_bar = 15

    return OrderBlockLifecycleState(
        finding=make_finding(
            side=side,
        ),
        state=state,
        created_bar=10,
        last_touch_bar=last_touch_bar,
        touch_count=touch_count,
        mitigation_count=mitigation_count,
        active=(
            state
            is not OrderBlockStateType.INVALIDATED
        ),
    )


def make_analyst_result() -> AnalystResult:
    analyst = OrderBlockAnalyst()

    return analyst.analyze_result(
        (
            make_state(),
        )
    )


def test_returns_analyst_result() -> None:
    result = make_analyst_result()

    assert isinstance(
        result,
        AnalystResult,
    )


def test_analyst_name() -> None:
    result = make_analyst_result()

    assert result.analyst == "OrderBlockAnalyst"


def test_analyst_id() -> None:
    result = make_analyst_result()

    assert result.analyst_id == "ORDER_BLOCK"


def test_payload_is_order_block_analysis() -> None:
    result = make_analyst_result()

    assert isinstance(
        result.payload,
        OrderBlockAnalysis,
    )


def test_confidence_matches_payload() -> None:
    result = make_analyst_result()

    assert (
        result.confidence
        == result.payload.confidence
    )


def test_opinion_matches_payload() -> None:
    result = make_analyst_result()

    assert (
        result.opinion
        == result.payload.opinion
    )


def test_evidence_matches_payload() -> None:
    result = make_analyst_result()

    assert (
        tuple(result.evidence)
        == result.payload.evidence
    )


def test_warnings_match_payload() -> None:
    result = make_analyst_result()

    assert (
        tuple(result.warnings)
        == result.payload.warnings
    )


def test_result_is_enabled() -> None:
    result = make_analyst_result()

    assert result.enabled is True


def test_empty_analysis_produces_valid_result() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze_result(
        ()
    )

    assert isinstance(
        result,
        AnalystResult,
    )
    assert isinstance(
        result.payload,
        OrderBlockAnalysis,
    )
    assert result.confidence == 0.0
    assert result.analyst_id == "ORDER_BLOCK"


def test_payload_is_frozen() -> None:
    result = make_analyst_result()

    assert isinstance(
        result.payload,
        OrderBlockAnalysis,
    )

    with pytest.raises(FrozenInstanceError):
        result.payload.confidence = 0.0  # type: ignore[misc]


def test_invalid_state_is_rejected() -> None:
    analyst = OrderBlockAnalyst()

    with pytest.raises(
        TypeError,
        match=(
            "states must contain "
            "OrderBlockLifecycleState objects"
        ),
    ):
        analyst.analyze_result(
            (
                None,  # type: ignore[arg-type]
            )
        )