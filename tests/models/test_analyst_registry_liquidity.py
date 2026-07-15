from __future__ import annotations

from imie.analysts import LiquidityAnalyst
from imie.models import (
    AnalystRegistry,
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


def make_registered_registry() -> AnalystRegistry:
    analyst = LiquidityAnalyst()
    pool = make_pool()

    result = analyst.analyze_result(
        liquidity=make_liquidity_result(pool),
        states=(make_state(pool),),
        sweeps=(),
    )

    registry = AnalystRegistry()
    registry.register(result)

    return registry


def test_registers_liquidity_analyst_result() -> None:
    registry = make_registered_registry()

    assert len(registry) == 1


def test_registry_contains_liquidity_result() -> None:
    registry = make_registered_registry()

    assert registry.contains("LIQUIDITY") is True


def test_registry_lookup_is_case_insensitive() -> None:
    registry = make_registered_registry()

    lower = registry.get("liquidity")
    upper = registry.get("LIQUIDITY")

    assert lower is not None
    assert lower is upper


def test_registry_returns_liquidity_payload() -> None:
    registry = make_registered_registry()

    result = registry.get("LIQUIDITY")

    assert result is not None
    assert isinstance(result.payload, LiquidityAnalysis)
    assert result.payload.active_pool_count == 1


def test_registry_collects_liquidity_evidence() -> None:
    registry = make_registered_registry()

    evidence = registry.evidence()

    assert any(
        "active liquidity pool" in item.lower()
        for item in evidence
    )


def test_registry_includes_liquidity_confidence() -> None:
    registry = make_registered_registry()

    result = registry.get("LIQUIDITY")

    assert result is not None
    assert registry.confidence() == result.confidence


def test_register_replaces_previous_liquidity_result() -> None:
    registry = make_registered_registry()

    first = registry.get("LIQUIDITY")

    assert first is not None

    registry.register(first)

    assert len(registry) == 1
    assert registry.get("LIQUIDITY") is first


def test_registry_clear_removes_liquidity_result() -> None:
    registry = make_registered_registry()

    registry.clear()

    assert len(registry) == 0
    assert registry.contains("LIQUIDITY") is False
    assert registry.get("LIQUIDITY") is None


def test_liquidity_result_uses_domain_analyst_id() -> None:
    registry = make_registered_registry()

    result = registry.get("LIQUIDITY")

    assert result is not None
    assert result.analyst == "LiquidityAnalyst"
    assert result.analyst_id == "LIQUIDITY"