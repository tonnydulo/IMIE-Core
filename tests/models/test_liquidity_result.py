from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    LiquidityBias,
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquidityResult,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)


def create_pool() -> LiquidityPool:

    point = LiquidityPoint(
        price=550.25,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=15,
        strength=3,
    )

    finding = LiquidityFinding(
        point=point,
        liquidity_type=LiquidityType.EQUAL_HIGH,
        importance=LiquidityImportance.MAJOR,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=92.0,
        state=LiquidityState.ACTIVE,
        reason="Equal High",
        evidence=("Equal High",),
        source="EqualHighDetector",
    )

    return LiquidityPool(
        price=550.25,
        upper=550.30,
        lower=550.20,
        side=LiquiditySide.BUY_SIDE,
        importance=LiquidityImportance.MAJOR,
        confidence=94.0,
        strength=5.0,
        findings=(finding,),
        reason="Institutional Pool",
        evidence=("Pool",),
    )


def create_result() -> LiquidityResult:

    pool = create_pool()

    return LiquidityResult(
        buy_side_pools=(pool,),
        sell_side_pools=(),
        nearest_buy_side=pool,
        nearest_sell_side=None,
        highest_confidence_pool=pool,
        highest_importance_pool=pool,
        active_pool_count=1,
        major_pool_count=1,
        average_confidence=94.0,
        institutional_bias=LiquidityBias.BUY_SIDE_DOMINANT,
        evidence=("Evidence",),
        warnings=(),
    )


def test_fields() -> None:

    result = create_result()

    assert result.active_pool_count == 1
    assert result.major_pool_count == 1
    assert result.average_confidence == 94.0


def test_is_frozen() -> None:

    result = create_result()

    with pytest.raises(FrozenInstanceError):
        result.active_pool_count = 2  # type: ignore[misc]


def test_total_pool_count() -> None:

    assert create_result().total_pool_count == 1


def test_has_buy_side() -> None:

    assert create_result().has_buy_side is True


def test_has_sell_side() -> None:

    assert create_result().has_sell_side is False


def test_has_major_liquidity() -> None:

    assert create_result().has_major_liquidity is True


def test_strongest_pool() -> None:

    result = create_result()

    assert (
        result.strongest_pool
        is result.highest_confidence_pool
    )


def test_invalid_bias() -> None:

    pool = create_pool()

    with pytest.raises(TypeError):

        LiquidityResult(
            buy_side_pools=(pool,),
            sell_side_pools=(),
            nearest_buy_side=pool,
            nearest_sell_side=None,
            highest_confidence_pool=pool,
            highest_importance_pool=pool,
            active_pool_count=1,
            major_pool_count=1,
            average_confidence=90.0,
            institutional_bias="RANDOM",
            evidence=(),
            warnings=(),
        )


def test_invalid_average_confidence() -> None:
    pool = create_pool()

    with pytest.raises(
        ValueError,
        match="average_confidence must be between 0 and 100",
    ):
        LiquidityResult(
            buy_side_pools=(pool,),
            sell_side_pools=(),
            nearest_buy_side=pool,
            nearest_sell_side=None,
            highest_confidence_pool=pool,
            highest_importance_pool=pool,
            active_pool_count=1,
            major_pool_count=1,
            average_confidence=120.0,
            institutional_bias=LiquidityBias.BUY_SIDE_DOMINANT,
            evidence=(),
            warnings=(),
        )