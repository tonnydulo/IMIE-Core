from __future__ import annotations

import pytest

from imie.engines.liquidity import LiquidityEngine
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


def make_pool(
    *,
    side: LiquiditySide,
    price: float,
    confidence: float = 90.0,
    strength: float = 5.0,
    importance: LiquidityImportance = LiquidityImportance.MINOR,
) -> LiquidityPool:

    point = LiquidityPoint(
        price=price,
        side=side,
        first_index=10,
        second_index=20,
        strength=3,
    )

    finding = LiquidityFinding(
        point=point,
        liquidity_type=(
            LiquidityType.EQUAL_HIGH
            if side is LiquiditySide.BUY_SIDE
            else LiquidityType.EQUAL_LOW
        ),
        importance=importance,
        location=LiquidityLocation.UNCLASSIFIED,
        confidence=confidence,
        state=LiquidityState.ACTIVE,
        reason="Liquidity",
        evidence=("Liquidity",),
        source="Detector",
    )

    return LiquidityPool(
        price=price,
        upper=price + 0.01,
        lower=price - 0.01,
        side=side,
        importance=importance,
        confidence=confidence,
        strength=strength,
        findings=(finding,),
        reason="Pool",
        evidence=("Pool",),
    )


def test_empty_result() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(())

    assert result.total_pool_count == 0
    assert result.active_pool_count == 0
    assert result.institutional_bias == "UNKNOWN"
    assert result.nearest_buy_side is None
    assert result.nearest_sell_side is None


def test_buy_side_split() -> None:

    engine = LiquidityEngine()

    buy = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=550.0,
    )

    result = engine.evaluate((buy,))

    assert len(result.buy_side_pools) == 1
    assert len(result.sell_side_pools) == 0


def test_sell_side_split() -> None:

    engine = LiquidityEngine()

    sell = make_pool(
        side=LiquiditySide.SELL_SIDE,
        price=545.0,
    )

    result = engine.evaluate((sell,))

    assert len(result.sell_side_pools) == 1
    assert len(result.buy_side_pools) == 0


def test_nearest_buy_side() -> None:

    engine = LiquidityEngine()

    higher = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=551,
    )

    lower = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=550,
    )

    result = engine.evaluate(
        (
            higher,
            lower,
        )
    )

    assert result.nearest_buy_side is lower


def test_nearest_sell_side() -> None:

    engine = LiquidityEngine()

    lower = make_pool(
        side=LiquiditySide.SELL_SIDE,
        price=544,
    )

    higher = make_pool(
        side=LiquiditySide.SELL_SIDE,
        price=546,
    )

    result = engine.evaluate(
        (
            lower,
            higher,
        )
    )

    assert result.nearest_sell_side is higher


def test_highest_confidence_pool() -> None:

    engine = LiquidityEngine()

    weak = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=550,
        confidence=80,
    )

    strong = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=551,
        confidence=95,
    )

    result = engine.evaluate(
        (
            weak,
            strong,
        )
    )

    assert (
        result.highest_confidence_pool
        is strong
    )


def test_highest_importance_pool() -> None:

    engine = LiquidityEngine()

    major = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=550,
        importance=LiquidityImportance.MAJOR,
    )

    minor = make_pool(
        side=LiquiditySide.BUY_SIDE,
        price=551,
        importance=LiquidityImportance.MINOR,
    )

    result = engine.evaluate(
        (
            major,
            minor,
        )
    )

    assert (
        result.highest_importance_pool
        is major
    )


def test_average_confidence() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
                confidence=80,
            ),
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=545,
                confidence=100,
            ),
        )
    )

    assert result.average_confidence == 90.0


def test_buy_side_bias() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
            ),
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=551,
            ),
        )
    )

    assert (
        result.institutional_bias
        == "BUY_SIDE_DOMINANT"
    )


def test_sell_side_bias() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=545,
            ),
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=544,
            ),
        )
    )

    assert (
        result.institutional_bias
        == "SELL_SIDE_DOMINANT"
    )


def test_balanced_bias() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
            ),
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=545,
            ),
        )
    )

    assert (
        result.institutional_bias
        == "BALANCED"
    )


def test_major_pool_count() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
                importance=LiquidityImportance.MAJOR,
            ),
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=545,
                importance=LiquidityImportance.MINOR,
            ),
        )
    )

    assert result.major_pool_count == 1


def test_evidence_generated() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
            ),
        )
    )

    assert len(result.evidence) > 0


def test_warning_for_no_buy_side() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.SELL_SIDE,
                price=545,
            ),
        )
    )

    assert (
        "No buy-side liquidity detected."
        in result.warnings
    )


def test_warning_for_no_sell_side() -> None:

    engine = LiquidityEngine()

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
            ),
        )
    )

    assert (
        "No sell-side liquidity detected."
        in result.warnings
    )


def test_warning_for_weak_confidence() -> None:

    engine = LiquidityEngine(
        weak_confidence_threshold=90.0,
    )

    result = engine.evaluate(
        (
            make_pool(
                side=LiquiditySide.BUY_SIDE,
                price=550,
                confidence=70,
            ),
        )
    )

    assert (
        "Average liquidity confidence is weak."
        in result.warnings
    )


def test_invalid_threshold() -> None:

    with pytest.raises(ValueError):

        LiquidityEngine(
            weak_confidence_threshold=120,
        )