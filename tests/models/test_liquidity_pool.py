from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)


def create_finding() -> LiquidityFinding:
    point = LiquidityPoint(
        price=550.25,
        side=LiquiditySide.BUY_SIDE,
        first_index=10,
        second_index=14,
        strength=2,
    )

    return LiquidityFinding(
        point=point,
        liquidity_type=LiquidityType.PREVIOUS_DAY_HIGH,
        importance=LiquidityImportance.INTERMEDIATE,
        location=LiquidityLocation.EXTERNAL,
        confidence=92.0,
        state=LiquidityState.ACTIVE,
        reason="Previous Day High.",
        evidence=("Untouched liquidity.",),
        source="PreviousDayDetector",
    )


def create_pool() -> LiquidityPool:
    finding = create_finding()

    return LiquidityPool(
        price=550.25,
        upper=550.30,
        lower=550.20,
        side=LiquiditySide.BUY_SIDE,
        importance=LiquidityImportance.INTERMEDIATE,
        confidence=95.0,
        strength=88.0,
        findings=(finding,),
        reason="Confluence of institutional liquidity.",
        evidence=("Previous Day High.",),
    )


def test_pool_fields() -> None:
    pool = create_pool()

    assert pool.price == 550.25
    assert pool.upper == 550.30
    assert pool.lower == 550.20
    assert pool.confidence == 95.0
    assert pool.strength == 88.0


def test_pool_is_frozen() -> None:
    pool = create_pool()

    with pytest.raises(FrozenInstanceError):
        pool.price = 600.0  # type: ignore[misc]


def test_finding_count() -> None:
    assert create_pool().finding_count == 1


def test_side_helpers() -> None:
    pool = create_pool()

    assert pool.is_buy_side is True
    assert pool.is_sell_side is False


def test_major_helper() -> None:
    major = LiquidityPool(
        price=550.25,
        upper=550.30,
        lower=550.20,
        side=LiquiditySide.BUY_SIDE,
        importance=LiquidityImportance.MAJOR,
        confidence=100.0,
        strength=100.0,
        findings=(create_finding(),),
        reason="Major pool.",
        evidence=("Weekly + Daily.",),
    )

    assert major.is_major is True


def test_pool_requires_findings() -> None:
    with pytest.raises(ValueError, match="at least one finding"):
        LiquidityPool(
            price=550.25,
            upper=550.30,
            lower=550.20,
            side=LiquiditySide.BUY_SIDE,
            importance=LiquidityImportance.MAJOR,
            confidence=95.0,
            strength=90.0,
            findings=(),
            reason="Pool",
            evidence=("Evidence",),
        )