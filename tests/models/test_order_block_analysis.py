from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    OrderBlockAnalysis,
    OrderBlockFinding,
    OrderBlockLifecycleState,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockStateType,
)


def make_finding(
    *,
    upper: float = 110.0,
    lower: float = 100.0,
    confidence: float = 90.0,
    strength: float = 85.0,
) -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=upper,
        lower=lower,
        side=OrderBlockSide.BULLISH,
        origin=OrderBlockOrigin.BOS,
        source_bar_index=10,
        displacement=5.0,
        strength=strength,
        confidence=confidence,
        reason="Institutional order block.",
        evidence=("Created.",),
        detector="Builder",
    )


def make_state(
    *,
    state: OrderBlockStateType = OrderBlockStateType.ACTIVE,
    upper: float = 110.0,
    lower: float = 100.0,
    confidence: float = 90.0,
    strength: float = 85.0,
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
            upper=upper,
            lower=lower,
            confidence=confidence,
            strength=strength,
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


def make_analysis() -> OrderBlockAnalysis:
    block = make_state()

    return OrderBlockAnalysis(
        nearest_bullish_block=block,
        nearest_bearish_block=None,
        strongest_block=block,
        active_blocks=(block,),
        confidence=87.5,
        opinion="Bullish institutional demand.",
        evidence=(
            "Fresh order block detected.",
        ),
    )


def test_constructs_analysis() -> None:
    analysis = make_analysis()

    assert analysis.nearest_bullish_block is not None
    assert analysis.strongest_block is not None
    assert analysis.confidence == 87.5


def test_confidence_clamped_low() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        confidence=-10.0,
    )

    assert analysis.confidence == 0.0


def test_confidence_clamped_high() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        confidence=150.0,
    )

    assert analysis.confidence == 100.0


def test_opinion_trimmed() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        opinion="  bullish  ",
    )

    assert analysis.opinion == "bullish"


def test_evidence_cleaned() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        evidence=(
            "",
            "A",
            "a",
            "B",
            " ",
        ),
    )

    assert analysis.evidence == (
        "A",
        "B",
    )


def test_warnings_cleaned() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        warnings=(
            "",
            "Warning",
            "warning",
        ),
    )

    assert analysis.warnings == (
        "Warning",
    )


def test_invalid_nearest_bullish_rejected() -> None:
    with pytest.raises(TypeError):
        OrderBlockAnalysis(
            nearest_bullish_block=object(),  # type: ignore[arg-type]
            nearest_bearish_block=None,
            strongest_block=None,
        )


def test_invalid_nearest_bearish_rejected() -> None:
    with pytest.raises(TypeError):
        OrderBlockAnalysis(
            nearest_bullish_block=None,
            nearest_bearish_block=object(),  # type: ignore[arg-type]
            strongest_block=None,
        )


def test_invalid_strongest_rejected() -> None:
    with pytest.raises(TypeError):
        OrderBlockAnalysis(
            nearest_bullish_block=None,
            nearest_bearish_block=None,
            strongest_block=object(),  # type: ignore[arg-type]
        )


def test_invalid_collection_member_rejected() -> None:
    with pytest.raises(TypeError):
        OrderBlockAnalysis(
            nearest_bullish_block=None,
            nearest_bearish_block=None,
            strongest_block=None,
            active_blocks=(object(),),  # type: ignore[arg-type]
        )


def test_active_count() -> None:
    block = make_state()

    analysis = OrderBlockAnalysis(
        nearest_bullish_block=block,
        nearest_bearish_block=None,
        strongest_block=block,
        active_blocks=(
            block,
            block,
        ),
    )

    assert analysis.active_count == 2


def test_tested_count() -> None:
    tested = make_state(
        state=OrderBlockStateType.TESTED,
    )

    analysis = OrderBlockAnalysis(
        nearest_bullish_block=tested,
        nearest_bearish_block=None,
        strongest_block=tested,
        tested_blocks=(tested,),
    )

    assert analysis.tested_count == 1


def test_mitigated_count() -> None:
    block = make_state(
        state=OrderBlockStateType.MITIGATED,
    )

    analysis = OrderBlockAnalysis(
        nearest_bullish_block=block,
        nearest_bearish_block=None,
        strongest_block=block,
        mitigated_blocks=(block,),
    )

    assert analysis.mitigated_count == 1


def test_invalidated_count() -> None:
    block = make_state(
        state=OrderBlockStateType.INVALIDATED,
    )

    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
        invalidated_blocks=(block,),
    )

    assert analysis.invalidated_count == 1


def test_has_active_blocks() -> None:
    assert make_analysis().has_active_blocks is True


def test_has_no_active_blocks() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
    )

    assert analysis.has_active_blocks is False


def test_has_bullish_block() -> None:
    assert make_analysis().has_bullish_block is True


def test_has_no_bullish_block() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
    )

    assert analysis.has_bullish_block is False


def test_has_bearish_block() -> None:
    block = make_state()

    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=block,
        strongest_block=block,
    )

    assert analysis.has_bearish_block is True


def test_has_strongest_block() -> None:
    assert make_analysis().has_strongest_block is True


def test_has_no_strongest_block() -> None:
    analysis = OrderBlockAnalysis(
        nearest_bullish_block=None,
        nearest_bearish_block=None,
        strongest_block=None,
    )

    assert analysis.has_strongest_block is False


def test_analysis_is_frozen() -> None:
    analysis = make_analysis()

    with pytest.raises(FrozenInstanceError):
        analysis.confidence = 0.0  # type: ignore[misc]