from __future__ import annotations

import pytest

from imie.analysts.liquidity_analyst import LiquidityAnalyst
from imie.models import (
    LiquidityAnalysis,
    LiquidityBias,
    LiquidityFinding,
    LiquidityImportance,
    LiquidityLocation,
    LiquidityPoint,
    LiquidityPool,
    LiquidityPoolState,
    LiquidityPoolStateType,
    LiquidityResult,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
    SweepDirection,
    SweepResult,
)


# ==========================================================
# Test Builders
# ==========================================================

def make_pool(
    side: LiquiditySide,
    price: float,
    confidence: float = 90.0,
    importance: LiquidityImportance = LiquidityImportance.MAJOR,
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
        source="UnitTest",
    )

    return LiquidityPool(
        price=price,
        upper=price + 0.05,
        lower=price - 0.05,
        side=side,
        importance=importance,
        confidence=confidence,
        strength=5.0,
        findings=(finding,),
        reason="Pool",
        evidence=("Pool",),
    )


def make_state(
    pool: LiquidityPool,
    state: LiquidityPoolStateType = LiquidityPoolStateType.ACTIVE,
) -> LiquidityPoolState:

    return LiquidityPoolState(
        pool=pool,
        state=state,
        created_bar=10,
        updated_bar=10,
        sweep_count=0,
        retest_count=0,
        evidence=("State",),
        warnings=(),
    )


def make_sweep(
    pool: LiquidityPool,
    swept: bool = False,
) -> SweepResult:

    return SweepResult(
        pool=pool,
        swept=swept,
        direction=(
            SweepDirection.BEARISH
            if swept
            else SweepDirection.NONE
        ),
        penetration_price=pool.upper if swept else None,
        close_price=pool.price,
        reclaimed=swept,
        confidence=95.0 if swept else 0.0,
        reason="Sweep",
        evidence=("Sweep",),
        warnings=(),
    )


def make_result(
    buy: tuple[LiquidityPool, ...],
    sell: tuple[LiquidityPool, ...],
) -> LiquidityResult:

    strongest = None

    if buy or sell:
        strongest = max(
            (*buy, *sell),
            key=lambda p: p.confidence,
        )

    return LiquidityResult(
        buy_side_pools=buy,
        sell_side_pools=sell,
        nearest_buy_side=buy[0] if buy else None,
        nearest_sell_side=sell[0] if sell else None,
        highest_confidence_pool=strongest,
        highest_importance_pool=strongest,
        active_pool_count=len(buy) + len(sell),
        major_pool_count=len(
            [
                p
                for p in (*buy, *sell)
                if p.importance is LiquidityImportance.MAJOR
            ]
        ),
        average_confidence=90.0 if strongest else 0.0,
        institutional_bias=LiquidityBias.BALANCED,
        evidence=("Liquidity",),
        warnings=(),
    )


# ==========================================================
# Tests
# ==========================================================

def test_returns_liquidity_analysis() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.BUY_SIDE,
        550.0,
    )

    analysis = analyst.analyze(
        liquidity=make_result((pool,), ()),
        states=(make_state(pool),),
        sweeps=(),
    )

    assert isinstance(
        analysis,
        LiquidityAnalysis,
    )


def test_buy_side_opinion() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
    )

    analysis = analyst.analyze(
        liquidity=make_result((pool,), ()),
        states=(make_state(pool),),
        sweeps=(),
    )

    assert "buy-side" in analysis.opinion.lower()


def test_sell_side_opinion() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.SELL_SIDE,
        540,
    )

    analysis = analyst.analyze(
        liquidity=make_result((), (pool,)),
        states=(make_state(pool),),
        sweeps=(),
    )

    assert "sell-side" in analysis.opinion.lower()


def test_balanced_opinion() -> None:

    analyst = LiquidityAnalyst()

    buy = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
    )

    sell = make_pool(
        LiquiditySide.SELL_SIDE,
        545,
    )

    analysis = analyst.analyze(
        liquidity=make_result((buy,), (sell,)),
        states=(
            make_state(buy),
            make_state(sell),
        ),
        sweeps=(),
    )

    assert "balanced" in analysis.opinion.lower()


def test_no_active_liquidity() -> None:

    analyst = LiquidityAnalyst()

    analysis = analyst.analyze(
        liquidity=make_result((), ()),
        states=(),
        sweeps=(),
    )

    assert analysis.active_pool_count == 0
    assert analysis.confidence == 0.0


def test_swept_pool_count() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
    )

    analysis = analyst.analyze(
        liquidity=make_result((pool,), ()),
        states=(
            make_state(
                pool,
                LiquidityPoolStateType.SWEPT,
            ),
        ),
        sweeps=(
            make_sweep(
                pool,
                swept=True,
            ),
        ),
    )

    assert analysis.swept_pool_count == 1


def test_strongest_pool_selected() -> None:

    analyst = LiquidityAnalyst()

    weak = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
        confidence=70,
    )

    strong = make_pool(
        LiquiditySide.BUY_SIDE,
        560,
        confidence=95,
    )

    analysis = analyst.analyze(
        liquidity=make_result(
            (weak, strong),
            (),
        ),
        states=(
            make_state(weak),
            make_state(strong),
        ),
        sweeps=(),
    )

    assert analysis.strongest_pool == strong


def test_invalid_liquidity_result() -> None:

    analyst = LiquidityAnalyst()

    with pytest.raises(TypeError):

        analyst.analyze(
            liquidity=None,  # type: ignore[arg-type]
            states=(),
            sweeps=(),
        )


def test_invalid_state_type() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
    )

    with pytest.raises(TypeError):

        analyst.analyze(
            liquidity=make_result((pool,), ()),
            states=(None,),  # type: ignore[arg-type]
            sweeps=(),
        )


def test_invalid_sweep_type() -> None:

    analyst = LiquidityAnalyst()

    pool = make_pool(
        LiquiditySide.BUY_SIDE,
        550,
    )

    with pytest.raises(TypeError):

        analyst.analyze(
            liquidity=make_result((pool,), ()),
            states=(make_state(pool),),
            sweeps=(None,),  # type: ignore[arg-type]
        )