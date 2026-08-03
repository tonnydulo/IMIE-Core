from __future__ import annotations

from imie.analysts import OrderBlockAnalyst
from imie.models import (
    AnalystRegistry,
    OrderBlockAnalysis,
    OrderBlockFinding,
    OrderBlockLifecycleState,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockStateType,
)


def make_finding(
    *,
    confidence: float = 92.0,
) -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=550.00,
        lower=549.50,
        side=OrderBlockSide.BULLISH,
        origin=OrderBlockOrigin.BOS,
        source_bar_index=10,
        displacement=0.50,
        strength=88.0,
        confidence=confidence,
        reason="Institutional order block.",
        evidence=(
            "Order block confirmed.",
        ),
        detector="OrderBlockBuilder",
    )


def make_state(
    *,
    confidence: float = 92.0,
) -> OrderBlockLifecycleState:
    return OrderBlockLifecycleState(
        finding=make_finding(
            confidence=confidence,
        ),
        state=OrderBlockStateType.ACTIVE,
        created_bar=10,
        last_touch_bar=None,
        touch_count=0,
        mitigation_count=0,
        active=True,
    )


def make_registered_registry() -> AnalystRegistry:
    analyst = OrderBlockAnalyst()

    result = analyst.analyze_result(
        (
            make_state(),
        )
    )

    registry = AnalystRegistry()
    registry.register(
        result
    )

    return registry


def test_registers_order_block_result() -> None:
    registry = make_registered_registry()

    assert len(registry) == 1


def test_registry_contains_order_block() -> None:
    registry = make_registered_registry()

    assert registry.contains(
        "ORDER_BLOCK"
    ) is True


def test_lookup_is_case_insensitive() -> None:
    registry = make_registered_registry()

    lower = registry.get(
        "order_block"
    )

    upper = registry.get(
        "ORDER_BLOCK"
    )

    assert lower is not None
    assert lower is upper


def test_registry_returns_order_block_payload() -> None:
    registry = make_registered_registry()

    result = registry.get(
        "ORDER_BLOCK"
    )

    assert result is not None
    assert isinstance(
        result.payload,
        OrderBlockAnalysis,
    )


def test_registry_preserves_confidence() -> None:
    registry = make_registered_registry()

    result = registry.get(
        "ORDER_BLOCK"
    )

    assert result is not None
    assert (
        registry.confidence()
        == result.confidence
    )


def test_registry_preserves_opinion() -> None:
    registry = make_registered_registry()

    result = registry.get(
        "ORDER_BLOCK"
    )

    assert result is not None
    assert (
        result.opinion
        == result.payload.opinion
    )


def test_registry_collects_order_block_evidence() -> None:
    registry = make_registered_registry()

    evidence = registry.evidence()

    assert any(
        "order block" in item.lower()
        for item in evidence
    )


def test_replaces_previous_order_block_result() -> None:
    analyst = OrderBlockAnalyst()
    registry = AnalystRegistry()

    first = analyst.analyze_result(
        (
            make_state(
                confidence=70.0,
            ),
        )
    )

    second = analyst.analyze_result(
        (
            make_state(
                confidence=96.0,
            ),
        )
    )

    registry.register(
        first
    )

    registry.register(
        second
    )

    result = registry.get(
        "ORDER_BLOCK"
    )

    assert len(registry) == 1
    assert result is second


def test_registry_clear_removes_order_block() -> None:
    registry = make_registered_registry()

    registry.clear()

    assert len(registry) == 0
    assert registry.contains(
        "ORDER_BLOCK"
    ) is False
    assert registry.get(
        "ORDER_BLOCK"
    ) is None


def test_result_uses_stable_domain_id() -> None:
    registry = make_registered_registry()

    result = registry.get(
        "ORDER_BLOCK"
    )

    assert result is not None
    assert result.analyst == "OrderBlockAnalyst"
    assert result.analyst_id == "ORDER_BLOCK"