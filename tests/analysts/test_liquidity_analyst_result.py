from __future__ import annotations

from imie.analysts import LiquidityAnalyst
from imie.models import (
    AnalystResult,
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
        evidence=("Equal-high liquidity confirmed.",),
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
        evidence=("Buy-side pool confirmed.",),
    )


def make_state(
    pool: LiquidityPool,
) -> LiquidityPoolState:
    return LiquidityPoolState(
        pool=pool,
        state=LiquidityPoolStateType.ACTIVE,
        created_bar=10,
        updated_bar=10,
        sweep_count=0,
        retest_count=0,
        evidence=("Lifecycle initialized.",),
        warnings=(),
    )


def make_liquidity_result(
    pool: LiquidityPool,
) -> LiquidityResult:
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
        evidence=("Buy-side liquidity detected.",),
        warnings=("No sell-side liquidity detected.",),
    )


def make_analyst_result() -> AnalystResult:
    analyst = LiquidityAnalyst()
    pool = make_pool()

    return analyst.analyze_result(
        liquidity=make_liquidity_result(pool),
        states=(make_state(pool),),
        sweeps=(),
    )


def test_analyze_result_returns_analyst_result() -> None:
    result = make_analyst_result()

    assert isinstance(result, AnalystResult)


def test_analyze_result_uses_liquidity_analyst_name() -> None:
    result = make_analyst_result()

    assert result.analyst == "LiquidityAnalyst"


def test_analyze_result_payload_is_liquidity_analysis() -> None:
    result = make_analyst_result()

    assert isinstance(
        result.payload,
        LiquidityAnalysis,
    )


def test_analyze_result_copies_opinion() -> None:
    result = make_analyst_result()

    assert result.opinion == result.payload.opinion


def test_analyze_result_copies_confidence() -> None:
    result = make_analyst_result()

    assert result.confidence == result.payload.confidence


def test_analyze_result_copies_evidence() -> None:
    result = make_analyst_result()

    assert tuple(result.evidence) == result.payload.evidence


def test_analyze_result_copies_warnings() -> None:
    result = make_analyst_result()

    assert tuple(result.warnings) == result.payload.warnings


def test_existing_analyze_method_remains_available() -> None:
    analyst = LiquidityAnalyst()
    pool = make_pool()

    analysis = analyst.analyze(
        liquidity=make_liquidity_result(pool),
        states=(make_state(pool),),
        sweeps=(),
    )

    assert isinstance(
        analysis,
        LiquidityAnalysis,
    )