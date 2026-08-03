from __future__ import annotations

import pytest

from imie.engines.order_blocks import (
    OrderBlockLifecycleEngine,
)
from imie.models import (
    MarketBar,
    OrderBlockFinding,
    OrderBlockLifecycleState,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockStateType,
)


def make_finding() -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=110.0,
        lower=100.0,
        side=OrderBlockSide.BULLISH,
        origin=OrderBlockOrigin.BOS,
        source_bar_index=10,
        displacement=5.0,
        strength=90.0,
        confidence=92.0,
        reason="Bullish order block.",
        evidence=("Created.",),
        detector="Builder",
    )


def make_state(
    *,
    state: OrderBlockStateType = OrderBlockStateType.NEW,
    touches: int = 0,
    mitigations: int = 0,
    active: bool = True,
) -> OrderBlockLifecycleState:
    return OrderBlockLifecycleState(
        finding=make_finding(),
        state=state,
        created_bar=10,
        last_touch_bar=None if touches == 0 else 20,
        touch_count=touches,
        mitigation_count=mitigations,
        active=active,
    )


def bar(
    *,
    low: float,
    high: float,
    close: float,
    index: int = 20,
) -> MarketBar:
    return MarketBar(
        symbol="SPY",
        timeframe="1m",
        timestamp=index,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
    )


def test_new_becomes_active() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(),
        latest_bar=bar(
            low=120,
            high=125,
            close=123,
        ),
    )

    assert result.state is OrderBlockStateType.ACTIVE


def test_active_without_touch_remains_active() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.ACTIVE,
        ),
        latest_bar=bar(
            low=120,
            high=125,
            close=124,
        ),
    )

    assert result.state is OrderBlockStateType.ACTIVE


def test_first_touch_becomes_tested() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.ACTIVE,
        ),
        latest_bar=bar(
            low=108,
            high=112,
            close=111,
        ),
    )

    assert result.state is OrderBlockStateType.TESTED
    assert result.touch_count == 1


def test_second_touch_increments_counter() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.TESTED,
            touches=1,
        ),
        latest_bar=bar(
            low=107,
            high=112,
            close=110,
        ),
    )

    assert result.touch_count == 2


def test_deep_penetration_becomes_mitigated() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.TESTED,
            touches=1,
        ),
        latest_bar=bar(
            low=101,
            high=112,
            close=105,
        ),
    )

    assert result.state is OrderBlockStateType.MITIGATED
    assert result.mitigation_count == 1


def test_completed_close_below_block_invalidates() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.MITIGATED,
            touches=2,
            mitigations=1,
        ),
        latest_bar=bar(
            low=95,
            high=102,
            close=98,
        ),
    )

    assert result.state is OrderBlockStateType.INVALIDATED
    assert result.active is False


def test_invalidated_is_terminal() -> None:
    engine = OrderBlockLifecycleEngine()

    state = make_state(
        state=OrderBlockStateType.INVALIDATED,
        active=False,
    )

    result = engine.transition(
        state=state,
        latest_bar=bar(
            low=150,
            high=155,
            close=154,
        ),
    )

    assert result is state


def test_invalid_state_type_rejected() -> None:
    engine = OrderBlockLifecycleEngine()

    with pytest.raises(TypeError):
        engine.transition(
            state=None,  # type: ignore[arg-type]
            latest_bar=bar(
                low=120,
                high=125,
                close=124,
            ),
        )


def test_invalid_bar_type_rejected() -> None:
    engine = OrderBlockLifecycleEngine()

    with pytest.raises(TypeError):
        engine.transition(
            state=make_state(),
            latest_bar=None,  # type: ignore[arg-type]
        )


def test_touch_updates_last_touch_bar() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.ACTIVE,
        ),
        latest_bar=bar(
            low=108,
            high=112,
            close=110,
            index=55,
        ),
    )

    assert result.last_touch_bar == 55


def test_no_touch_does_not_change_last_touch_bar() -> None:
    engine = OrderBlockLifecycleEngine()

    state = make_state(
        state=OrderBlockStateType.ACTIVE,
    )

    result = engine.transition(
        state=state,
        latest_bar=bar(
            low=120,
            high=125,
            close=123,
        ),
    )

    assert result.last_touch_bar is None


def test_transition_returns_new_object() -> None:
    engine = OrderBlockLifecycleEngine()

    original = make_state()

    updated = engine.transition(
        state=original,
        latest_bar=bar(
            low=120,
            high=125,
            close=123,
        ),
    )

    assert updated is not original


def test_mitigation_counter_accumulates() -> None:
    engine = OrderBlockLifecycleEngine()

    result = engine.transition(
        state=make_state(
            state=OrderBlockStateType.MITIGATED,
            touches=3,
            mitigations=1,
        ),
        latest_bar=bar(
            low=100.5,
            high=111,
            close=104,
        ),
    )

    assert result.mitigation_count == 2