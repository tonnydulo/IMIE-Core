from dataclasses import FrozenInstanceError

import pytest

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
        reason="Confirmed equal-high liquidity.",
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
        reason="Institutional buy-side liquidity pool.",
        evidence=("Buy-side liquidity pool confirmed.",),
    )


def make_state(
    *,
    state: LiquidityPoolStateType = LiquidityPoolStateType.ACTIVE,
    created_bar: int = 10,
    updated_bar: int = 10,
    sweep_count: int = 0,
    retest_count: int = 0,
    evidence: tuple[str, ...] = ("Pool lifecycle initialized.",),
    warnings: tuple[str, ...] = (),
) -> LiquidityPoolState:
    return LiquidityPoolState(
        pool=make_pool(),
        state=state,
        created_bar=created_bar,
        updated_bar=updated_bar,
        sweep_count=sweep_count,
        retest_count=retest_count,
        evidence=evidence,
        warnings=warnings,
    )


def test_liquidity_pool_state_fields() -> None:
    pool_state = make_state()

    assert pool_state.state is LiquidityPoolStateType.ACTIVE
    assert pool_state.created_bar == 10
    assert pool_state.updated_bar == 10
    assert pool_state.sweep_count == 0
    assert pool_state.retest_count == 0


def test_liquidity_pool_state_is_frozen() -> None:
    pool_state = make_state()

    with pytest.raises(FrozenInstanceError):
        pool_state.updated_bar = 20  # type: ignore[misc]


def test_active_helper() -> None:
    pool_state = make_state(
        state=LiquidityPoolStateType.ACTIVE,
    )

    assert pool_state.is_active is True
    assert pool_state.is_swept is False
    assert pool_state.is_retested is False
    assert pool_state.is_consumed is False
    assert pool_state.is_retired is False


def test_swept_helper() -> None:
    pool_state = make_state(
        state=LiquidityPoolStateType.SWEPT,
        updated_bar=15,
        sweep_count=1,
    )

    assert pool_state.is_swept is True
    assert pool_state.is_active is False


def test_retested_helper() -> None:
    pool_state = make_state(
        state=LiquidityPoolStateType.RETESTED,
        updated_bar=20,
        sweep_count=1,
        retest_count=1,
    )

    assert pool_state.is_retested is True
    assert pool_state.is_swept is False


def test_consumed_helper() -> None:
    pool_state = make_state(
        state=LiquidityPoolStateType.CONSUMED,
        updated_bar=25,
        sweep_count=1,
        retest_count=1,
    )

    assert pool_state.is_consumed is True
    assert pool_state.is_retired is False


def test_retired_helper() -> None:
    pool_state = make_state(
        state=LiquidityPoolStateType.RETIRED,
        updated_bar=30,
        sweep_count=1,
        retest_count=1,
    )

    assert pool_state.is_retired is True
    assert pool_state.is_consumed is False


def test_age_calculation() -> None:
    pool_state = make_state(
        created_bar=10,
        updated_bar=25,
    )

    assert pool_state.age == 15


def test_rejects_invalid_pool_type() -> None:
    with pytest.raises(
        TypeError,
        match="pool must be a LiquidityPool",
    ):
        LiquidityPoolState(
            pool="not-a-pool",  # type: ignore[arg-type]
            state=LiquidityPoolStateType.ACTIVE,
            created_bar=10,
            updated_bar=10,
            sweep_count=0,
            retest_count=0,
            evidence=("Initialized.",),
            warnings=(),
        )


def test_rejects_invalid_state_type() -> None:
    with pytest.raises(
        TypeError,
        match="state must be a LiquidityPoolStateType",
    ):
        LiquidityPoolState(
            pool=make_pool(),
            state="ACTIVE",  # type: ignore[arg-type]
            created_bar=10,
            updated_bar=10,
            sweep_count=0,
            retest_count=0,
            evidence=("Initialized.",),
            warnings=(),
        )


def test_rejects_negative_created_bar() -> None:
    with pytest.raises(
        ValueError,
        match="created_bar cannot be negative",
    ):
        make_state(
            created_bar=-1,
            updated_bar=0,
        )


def test_rejects_updated_bar_before_created_bar() -> None:
    with pytest.raises(
        ValueError,
        match="updated_bar cannot precede created_bar",
    ):
        make_state(
            created_bar=10,
            updated_bar=9,
        )


def test_rejects_negative_sweep_count() -> None:
    with pytest.raises(
        ValueError,
        match="sweep_count cannot be negative",
    ):
        make_state(
            sweep_count=-1,
        )


def test_rejects_negative_retest_count() -> None:
    with pytest.raises(
        ValueError,
        match="retest_count cannot be negative",
    ):
        make_state(
            retest_count=-1,
        )


def test_rejects_empty_evidence_entry() -> None:
    with pytest.raises(
        ValueError,
        match="Evidence entries cannot be empty",
    ):
        make_state(
            evidence=("Initialized.", ""),
        )


def test_rejects_empty_warning_entry() -> None:
    with pytest.raises(
        ValueError,
        match="Warning entries cannot be empty",
    ):
        make_state(
            warnings=("",),
        )