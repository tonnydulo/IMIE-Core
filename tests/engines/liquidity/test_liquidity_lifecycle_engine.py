from __future__ import annotations

from dataclasses import replace

import pytest

from imie.engines.liquidity import LiquidityLifecycleEngine
from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquidityPoolState,
    LiquidityPoolStateType,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    SweepDirection,
    SweepResult,
)


def make_pool() -> LiquidityPool:
    point = LiquidityPoint(
        price=550.00,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=20,
        strength=3,
    )

    finding = LiquidityFinding(
        point=point,
        liquidity_type=LiquidityType.EQUAL_HIGH,
        importance=LiquidityImportance.MAJOR,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=92.0,
        state=LiquidityState.ACTIVE,
        reason="Equal-high liquidity.",
        evidence=("Equal highs confirmed.",),
        source="EqualHighDetector",
    )

    return LiquidityPool(
        price=550.00,
        upper=550.05,
        lower=549.95,
        side=LiquiditySide.BUY_SIDE,
        importance=LiquidityImportance.MAJOR,
        confidence=94.0,
        strength=5.0,
        findings=(finding,),
        reason="Institutional liquidity pool.",
        evidence=("Pool created.",),
    )


def make_state(
    *,
    state: LiquidityPoolStateType = LiquidityPoolStateType.ACTIVE,
    updated_bar: int = 10,
    sweep_count: int = 0,
) -> LiquidityPoolState:
    return LiquidityPoolState(
        pool=make_pool(),
        state=state,
        created_bar=10,
        updated_bar=updated_bar,
        sweep_count=sweep_count,
        retest_count=0,
        evidence=("Lifecycle initialized.",),
        warnings=(),
    )


def make_sweep(
    *,
    pool: LiquidityPool,
    swept: bool,
) -> SweepResult:
    return SweepResult(
        pool=pool,
        swept=swept,
        direction=(
            SweepDirection.BEARISH
            if swept
            else SweepDirection.NONE
        ),
        penetration_price=550.10 if swept else None,
        close_price=550.00,
        reclaimed=swept,
        confidence=95.0 if swept else 0.0,
        reason=(
            "Confirmed liquidity sweep."
            if swept
            else "No confirmed sweep."
        ),
        evidence=("Sweep evaluation.",),
        warnings=(),
    )


def test_active_without_sweep_remains_active() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state()

    result = engine.transition(
        previous=previous,
        sweep=make_sweep(
            pool=previous.pool,
            swept=False,
        ),
        current_bar=11,
    )

    assert result.state is LiquidityPoolStateType.ACTIVE
    assert result.sweep_count == 0
    assert result.updated_bar == 11


def test_active_transitions_to_swept() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state()

    result = engine.transition(
        previous=previous,
        sweep=make_sweep(
            pool=previous.pool,
            swept=True,
        ),
        current_bar=11,
    )

    assert result.state is LiquidityPoolStateType.SWEPT
    assert result.sweep_count == 1
    assert result.created_bar == previous.created_bar
    assert result.updated_bar == 11


def test_swept_state_does_not_increment_again() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state(
        state=LiquidityPoolStateType.SWEPT,
        sweep_count=1,
    )

    result = engine.transition(
        previous=previous,
        sweep=make_sweep(
            pool=previous.pool,
            swept=True,
        ),
        current_bar=12,
    )

    assert result.state is LiquidityPoolStateType.SWEPT
    assert result.sweep_count == 1


def test_created_bar_is_preserved() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state()

    result = engine.transition(
        previous=previous,
        sweep=make_sweep(
            pool=previous.pool,
            swept=False,
        ),
        current_bar=20,
    )

    assert result.created_bar == previous.created_bar


def test_rejects_backward_bar_progression() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state(
        updated_bar=20,
    )

    with pytest.raises(
        ValueError,
        match="current_bar",
    ):
        engine.transition(
            previous=previous,
            sweep=make_sweep(
                pool=previous.pool,
                swept=False,
            ),
            current_bar=19,
        )


def test_rejects_mismatched_pool() -> None:
    engine = LiquidityLifecycleEngine()

    previous = make_state()

    other_pool = replace(
        previous.pool,
        price=560.00,
    )

    with pytest.raises(
        ValueError,
        match="pool must match",
    ):
        engine.transition(
            previous=previous,
            sweep=make_sweep(
                pool=other_pool,
                swept=False,
            ),
            current_bar=11,
        )


def test_rejects_invalid_previous_type() -> None:
    engine = LiquidityLifecycleEngine()

    with pytest.raises(TypeError):
        engine.transition(
            previous=None,  # type: ignore[arg-type]
            sweep=make_sweep(
                pool=make_pool(),
                swept=False,
            ),
            current_bar=10,
        )


def test_rejects_invalid_sweep_type() -> None:
    engine = LiquidityLifecycleEngine()

    with pytest.raises(TypeError):
        engine.transition(
            previous=make_state(),
            sweep=None,  # type: ignore[arg-type]
            current_bar=10,
        )