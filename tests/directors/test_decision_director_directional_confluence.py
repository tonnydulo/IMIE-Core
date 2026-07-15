from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from imie.directors.decision_director import (
    DecisionDirector,
    DecisionDirectorConfig,
)
from imie.models import (
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    DirectorDecision,
    TradePlan,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_LIQUIDITY,
    ANALYST_ORDER_BLOCK,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_STRUCTURE,
    ANALYST_TREND,
)
from imie.utils.constants import (
    LIFECYCLE_EXTENDED,
    LIFECYCLE_READY,
    TREND_BEARISH,
    TREND_BULLISH,
    TREND_NEUTRAL,
)


class AcceptancePayload:
    def __init__(
        self,
        accepted: bool,
    ) -> None:
        self.accepted = accepted


def make_freshness() -> DataFreshness:
    now = datetime.now(
        timezone.utc
    )

    return DataFreshness(
        status="FRESH",
        actionable=True,
        checked_at=now,
        quote_timestamp=now,
        latest_bar_timestamp=now,
        quote_age_seconds=0.0,
        bar_age_seconds=0.0,
        quote_bar_gap_seconds=0.0,
        quote_is_fresh=True,
        bar_is_fresh=True,
        timestamps_aligned=True,
        reason="Market data is fresh.",
    )


def make_trade_plan(
    *,
    direction: str = "long",
    valid: bool = True,
    actionable: bool = True,
) -> TradePlan:
    return TradePlan(
        symbol="SPY",
        strategy="PULLBACK_TO_CORE",
        direction=direction,
        valid=valid,
        actionable=actionable,
        decision=(
            "READY"
            if valid and actionable
            else "PASS"
        ),
        entry=500.0 if valid else None,
        stop=499.0 if valid else None,
        target1=501.0 if valid else None,
        target2=502.0 if valid else None,
        risk_per_share=1.0 if valid else None,
        reward1_per_share=1.0 if valid else None,
        reward2_per_share=2.0 if valid else None,
        rr1=1.0 if valid else None,
        rr2=2.0 if valid else None,
        quality=90 if valid else 0,
        confidence=90.0 if valid else 0.0,
        reasons=(
            [
                "Risk validation passed.",
            ]
            if valid
            else [
                "Risk validation failed.",
            ]
        ),
        warnings=[],
        narrative="TradePlan test fixture.",
    )


def make_result(
    *,
    analyst_id: str,
    analyst: str,
    opinion: str,
    confidence: float = 90.0,
    enabled: bool = True,
    payload: Any | None = None,
) -> AnalystResult:
    return AnalystResult(
        analyst_id=analyst_id,
        analyst=analyst,
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        evidence=[],
        warnings=[],
        payload=payload,
    )


def make_ready_registry(
    *,
    trend: str = TREND_BULLISH,
    plan_direction: str = "long",
    confidence: float = 90.0,
) -> AnalystRegistry:
    registry = AnalystRegistry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="TrendAnalyst",
            opinion=trend,
            confidence=confidence,
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="SetupLifecycleAnalyst",
            opinion=LIFECYCLE_READY,
            confidence=confidence,
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="AcceptanceAnalyst",
            opinion="STRONG",
            confidence=confidence,
            payload=AcceptancePayload(
                accepted=True
            ),
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_RISK,
            analyst="RiskAnalyst",
            opinion="READY",
            confidence=confidence,
            payload=make_trade_plan(
                direction=plan_direction
            ),
        )
    )

    return registry


def register_structure(
    registry: AnalystRegistry,
    opinion: str,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_STRUCTURE,
            analyst="StructureAnalyst",
            opinion=opinion,
        )
    )


def register_liquidity(
    registry: AnalystRegistry,
    opinion: str,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_LIQUIDITY,
            analyst="LiquidityAnalyst",
            opinion=opinion,
        )
    )


def register_order_block(
    registry: AnalystRegistry,
    opinion: str,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_ORDER_BLOCK,
            analyst="OrderBlockAnalyst",
            opinion=opinion,
        )
    )


def evaluate(
    registry: AnalystRegistry,
    *,
    minimum_ready_confidence: float = 60.0,
):
    director = DecisionDirector(
        config=DecisionDirectorConfig(
            minimum_ready_confidence=(
                minimum_ready_confidence
            )
        )
    )

    return director.evaluate(
        context=None,  # type: ignore[arg-type]
        freshness=make_freshness(),
        registry=registry,
    )


def add_all_bullish(
    registry: AnalystRegistry,
) -> None:
    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity demand remains active.",
    )

    register_order_block(
        registry,
        "Bullish order block confirmed.",
    )


def add_all_bearish(
    registry: AnalystRegistry,
) -> None:
    register_structure(
        registry,
        "Bearish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity supply remains active.",
    )

    register_order_block(
        registry,
        "Bearish order block confirmed.",
    )


def test_bullish_confluence_boosts_long_trade() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 98.0

    assert (
        "Applied institutional confidence adjustment is +8."
        in result.reasons
    )


def test_bearish_confluence_boosts_short_trade() -> None:
    registry = make_ready_registry(
        trend=TREND_BEARISH,
        plan_direction="short",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 98.0


def test_bearish_confluence_does_not_boost_long_trade() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Applied institutional confidence adjustment is +0."
        in result.reasons
    )

    assert (
        "Institutional confluence opposes the intended bullish trade."
        in result.warnings
    )


def test_bullish_confluence_does_not_boost_short_trade() -> None:
    registry = make_ready_registry(
        trend=TREND_BEARISH,
        plan_direction="short",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional confluence opposes the intended bearish trade."
        in result.warnings
    )


def test_unknown_confluence_does_not_boost_trade() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional direction is unresolved; no directional "
        "confluence bonus is available."
        in result.warnings
    )


def test_neutral_confluence_does_not_boost_trade() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Neutral structure.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity remains balanced.",
    )

    register_order_block(
        registry,
        "Institutional order flow remains balanced.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional direction is neutral; no directional "
        "confluence bonus is available."
        in result.warnings
    )


def test_two_aligned_domains_add_five() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity demand remains active.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 95.0


def test_one_aligned_domain_adds_two() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 92.0


def test_two_bullish_one_bearish_adds_five() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity supply remains active.",
    )

    register_order_block(
        registry,
        "Bullish order block confirmed.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 95.0

    assert (
        "Institutional conflict is present within the "
        "confluence result."
        in result.warnings
    )


def test_conflicting_domain_does_not_add_weight() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity supply remains active.",
    )

    register_order_block(
        registry,
        "Bullish order block confirmed.",
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional confluence score is 70/100."
        in result.reasons
    )


def test_tied_bullish_and_bearish_votes_give_no_bonus() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity supply remains active.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional dominant direction is UNKNOWN."
        in result.reasons
    )


def test_confidence_is_capped_at_one_hundred() -> None:
    registry = make_ready_registry(
        confidence=99.0
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 100.0


def test_alignment_reason_is_present() -> None:
    registry = make_ready_registry()

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional confluence aligns with the intended "
        "bullish trade."
        in result.reasons
    )


def test_agreement_count_is_reported() -> None:
    registry = make_ready_registry()

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional agreement count is 3."
        in result.reasons
    )


def test_conflict_count_is_reported() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        "Bullish structure confirmed.",
    )

    register_liquidity(
        registry,
        "Institutional liquidity supply remains active.",
    )

    register_order_block(
        registry,
        "Bullish order block confirmed.",
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional conflict count is 1."
        in result.reasons
    )


def test_trade_plan_direction_takes_priority() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="short",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional confluence opposes the intended bearish trade."
        in result.warnings
    )


def test_confluence_does_not_override_neutral_trend() -> None:
    registry = make_ready_registry(
        trend=TREND_NEUTRAL,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.IGNORE
    assert result.actionable is False


def test_confluence_does_not_override_waiting_setup() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="SetupLifecycleAnalyst",
            opinion=LIFECYCLE_EXTENDED,
        )
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_confluence_does_not_override_failed_acceptance() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="AcceptanceAnalyst",
            opinion="NONE",
            confidence=0.0,
            payload=AcceptancePayload(
                accepted=False
            ),
        )
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_confluence_does_not_override_invalid_trade_plan() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_RISK,
            analyst="RiskAnalyst",
            opinion="PASS",
            confidence=0.0,
            payload=make_trade_plan(
                valid=False,
                actionable=False,
            ),
        )
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False

