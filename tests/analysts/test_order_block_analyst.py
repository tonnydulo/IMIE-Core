from __future__ import annotations

import pytest

from imie.analysts.order_block_analyst import (
    OrderBlockAnalyst,
)
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
    side: OrderBlockSide = OrderBlockSide.BULLISH,
    upper: float = 110.0,
    lower: float = 100.0,
    confidence: float = 90.0,
    strength: float = 85.0,
) -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=upper,
        lower=lower,
        side=side,
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
    side: OrderBlockSide = OrderBlockSide.BULLISH,
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
            side=side,
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


def test_empty_analysis() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(())

    assert isinstance(
        result,
        OrderBlockAnalysis,
    )

    assert result.active_count == 0
    assert result.confidence == 0.0
    assert result.has_active_blocks is False


def test_single_bullish_block() -> None:
    analyst = OrderBlockAnalyst()

    block = make_state()

    result = analyst.analyze((block,))

    assert (
        result.nearest_bullish_block
        is block
    )

    assert result.has_bullish_block is True


def test_single_bearish_block() -> None:
    analyst = OrderBlockAnalyst()

    block = make_state(
        side=OrderBlockSide.BEARISH,
    )

    result = analyst.analyze((block,))

    assert (
        result.nearest_bearish_block
        is block
    )

    assert result.has_bearish_block is True


def test_strongest_block_selected() -> None:
    analyst = OrderBlockAnalyst()

    weak = make_state(
        confidence=70.0,
    )

    strong = make_state(
        upper=130,
        lower=120,
        confidence=96.0,
    )

    result = analyst.analyze(
        (
            weak,
            strong,
        )
    )

    assert (
        result.strongest_block
        is strong
    )


def test_multiple_active_blocks() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
            make_state(
                upper=130,
                lower=120,
            ),
        )
    )

    assert result.active_count == 2


def test_tested_block_count() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(
                state=OrderBlockStateType.TESTED,
            ),
        )
    )

    assert result.tested_count == 1


def test_mitigated_block_count() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(
                state=OrderBlockStateType.MITIGATED,
            ),
        )
    )

    assert result.mitigated_count == 1


def test_invalidated_block_count() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(
                state=OrderBlockStateType.INVALIDATED,
            ),
        )
    )

    assert result.invalidated_count == 1


def test_no_active_warning() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(
                state=OrderBlockStateType.INVALIDATED,
            ),
        )
    )

    assert result.warnings


def test_confidence_zero_without_blocks() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(())

    assert result.confidence == 0.0


def test_confidence_single_block() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
        )
    )

    assert result.confidence >= 60.0


def test_confidence_multiple_blocks() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
            make_state(
                upper=130,
                lower=120,
            ),
        )
    )

    assert result.confidence >= 80.0


def test_invalid_state_rejected() -> None:
    analyst = OrderBlockAnalyst()

    with pytest.raises(TypeError):
        analyst.analyze(
            (
                None,  # type: ignore[arg-type]
            )
        )


def test_nearest_bullish_selected() -> None:
    analyst = OrderBlockAnalyst()

    near = make_state(
        upper=102,
        lower=100,
    )

    far = make_state(
        upper=150,
        lower=145,
    )

    result = analyst.analyze(
        (
            far,
            near,
        )
    )

    assert (
        result.nearest_bullish_block
        is near
    )


def test_nearest_bearish_selected() -> None:
    analyst = OrderBlockAnalyst()

    high = make_state(
        side=OrderBlockSide.BEARISH,
        upper=200,
        lower=190,
    )

    low = make_state(
        side=OrderBlockSide.BEARISH,
        upper=150,
        lower=140,
    )

    result = analyst.analyze(
        (
            low,
            high,
        )
    )

    assert (
        result.nearest_bearish_block
        is low
    )


def test_opinion_present() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
        )
    )

    assert result.opinion


def test_evidence_present() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
        )
    )

    assert result.evidence


def test_duplicate_evidence_removed() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
            make_state(),
        )
    )

    assert len(result.evidence) == len(
        set(result.evidence)
    )


def test_analysis_type() -> None:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze(
        (
            make_state(),
        )
    )

    assert isinstance(
        result,
        OrderBlockAnalysis,
    )