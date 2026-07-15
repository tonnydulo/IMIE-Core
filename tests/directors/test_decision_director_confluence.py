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
    valid: bool = True,
    actionable: bool = True,
) -> TradePlan:
    return TradePlan(
        symbol="SPY",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        valid=valid,
        actionable=actionable,
        decision=(
            "READY"
            if valid and actionable
            else "PASS"
        ),
        entry=500.00 if valid else None,
        stop=499.00 if valid else None,
        target1=501.00 if valid else None,
        target2=502.00 if valid else None,
        risk_per_share=1.00 if valid else None,
        reward1_per_share=1.00 if valid else None,
        reward2_per_share=2.00 if valid else None,
        rr1=1.00 if valid else None,
        rr2=2.00 if valid else None,
        quality=90 if valid else 0,
        confidence=90.0 if valid else 0.0,
        reasons=(
            [
                "Risk validation passed.",
                "Projected Target 2 provides 2.00R.",
            ]
            if valid
            else [
                "Risk validation failed.",
            ]
        ),
        warnings=(
            []
            if valid
            else [
                "Risk requirements were not satisfied.",
            ]
        ),
        narrative=(
            "A valid TradePlan is available."
            if valid
            else "The TradePlan is invalid."
        ),
    )


def make_result(
    *,
    analyst_id: str,
    analyst: str,
    opinion: str,
    confidence: float = 90.0,
    enabled: bool = True,
    evidence: list[str] | None = None,
    warnings: list[str] | None = None,
    payload: Any | None = None,
) -> AnalystResult:
    return AnalystResult(
        analyst_id=analyst_id,
        analyst=analyst,
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        evidence=evidence or [],
        warnings=warnings or [],
        payload=payload,
    )


def make_ready_registry(
    *,
    confidence: float = 90.0,
) -> AnalystRegistry:
    registry = AnalystRegistry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="TrendAnalyst",
            opinion=TREND_BULLISH,
            confidence=confidence,
            evidence=[
                "Bullish trend confirmed.",
            ],
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="SetupLifecycleAnalyst",
            opinion=LIFECYCLE_READY,
            confidence=confidence,
            evidence=[
                "Setup lifecycle is READY.",
            ],
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="AcceptanceAnalyst",
            opinion="STRONG",
            confidence=confidence,
            evidence=[
                "Completed-candle acceptance confirmed.",
            ],
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
            evidence=[
                "Risk analysis produced an actionable TradePlan.",
            ],
            payload=make_trade_plan(),
        )
    )

    return registry


def register_structure(
    registry: AnalystRegistry,
    *,
    opinion: str = "Bullish structure confirmed.",
    confidence: float = 90.0,
    enabled: bool = True,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_STRUCTURE,
            analyst="StructureAnalyst",
            opinion=opinion,
            confidence=confidence,
            enabled=enabled,
        )
    )


def register_liquidity(
    registry: AnalystRegistry,
    *,
    opinion: str = (
        "Institutional liquidity demand remains active."
    ),
    confidence: float = 90.0,
    enabled: bool = True,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_LIQUIDITY,
            analyst="LiquidityAnalyst",
            opinion=opinion,
            confidence=confidence,
            enabled=enabled,
        )
    )


def register_order_block(
    registry: AnalystRegistry,
    *,
    opinion: str = (
        "Active institutional demand remains below price."
    ),
    confidence: float = 90.0,
    enabled: bool = True,
) -> None:
    registry.register(
        make_result(
            analyst_id=ANALYST_ORDER_BLOCK,
            analyst="OrderBlockAnalyst",
            opinion=opinion,
            confidence=confidence,
            enabled=enabled,
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
            ),
        )
    )

    return director.evaluate(
        context=None,  # type: ignore[arg-type]
        freshness=make_freshness(),
        registry=registry,
    )


def test_no_institutional_results_gives_zero_adjustment() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 90.0

    assert (
        "Institutional confidence adjustment is +0."
        in result.reasons
    )


def test_structure_only_adds_two_points() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 92.0

    assert (
        "Institutional confidence adjustment is +2."
        in result.reasons
    )


def test_liquidity_only_adds_two_points() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 92.0


def test_order_block_only_adds_two_points() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 92.0


@pytest.mark.parametrize(
    (
        "first",
        "second",
    ),
    [
        (
            "structure",
            "liquidity",
        ),
        (
            "structure",
            "order_block",
        ),
        (
            "liquidity",
            "order_block",
        ),
    ],
)
def test_two_supporting_domains_add_five_points(
    first: str,
    second: str,
) -> None:
    registry = make_ready_registry()

    registrations = {
        "structure": register_structure,
        "liquidity": register_liquidity,
        "order_block": register_order_block,
    }

    registrations[
        first
    ](
        registry
    )

    registrations[
        second
    ](
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 95.0

    assert (
        "Institutional confidence adjustment is +5."
        in result.reasons
    )


def test_three_supporting_domains_add_eight_points() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.confidence == 98.0

    assert (
        "Institutional confidence adjustment is +8."
        in result.reasons
    )


def test_final_confidence_is_capped_at_one_hundred() -> None:
    registry = make_ready_registry(
        confidence=99.0
    )

    register_structure(
        registry,
        confidence=99.0,
    )

    register_liquidity(
        registry,
        confidence=99.0,
    )

    register_order_block(
        registry,
        confidence=99.0,
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 100.0


def test_confluence_score_is_reported() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional confluence score is 70/100."
        in result.reasons
    )


def test_confluence_evidence_reaches_decision_result() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "Structure confirms institutional continuation."
        in result.reasons
    )

    assert (
        "Liquidity supports institutional continuation."
        in result.reasons
    )

    assert (
        "Order Blocks support institutional continuation."
        in result.reasons
    )

    assert (
        "Three institutional domains support the setup."
        in result.reasons
    )


def test_no_support_warning_reaches_decision_result() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert (
        "No institutional agreement detected."
        in result.warnings
    )


def test_one_support_warning_reaches_decision_result() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "Only one institutional domain supports the setup."
        in result.warnings
    )


def test_two_supporting_domains_have_no_confluence_warning() -> None:
    registry = make_ready_registry()

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    result = evaluate(
        registry
    )

    assert (
        "No institutional agreement detected."
        not in result.warnings
    )

    assert (
        "Only one institutional domain supports the setup."
        not in result.warnings
    )


def test_missing_optional_analysts_do_not_block_ready() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_disabled_optional_analysts_do_not_count() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        enabled=False,
    )

    register_liquidity(
        registry,
        enabled=False,
    )

    register_order_block(
        registry,
        enabled=False,
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0

    assert (
        "Institutional confidence adjustment is +0."
        in result.reasons
    )


def test_unknown_optional_opinions_do_not_count() -> None:
    registry = make_ready_registry()

    register_structure(
        registry,
        opinion="Structure unavailable.",
    )

    register_liquidity(
        registry,
        opinion="Liquidity remains balanced.",
    )

    register_order_block(
        registry,
        opinion="No actionable order blocks.",
    )

    result = evaluate(
        registry
    )

    assert result.confidence == 90.0


def test_confluence_does_not_override_neutral_trend() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="TrendAnalyst",
            opinion=TREND_NEUTRAL,
            confidence=90.0,
        )
    )

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.IGNORE
    assert result.actionable is False
    assert result.confidence == 90.0


def test_confluence_does_not_override_waiting_setup() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="SetupLifecycleAnalyst",
            opinion=LIFECYCLE_EXTENDED,
            confidence=90.0,
        )
    )

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
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

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_confluence_does_not_override_invalid_risk_plan() -> None:
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

    register_structure(
        registry
    )

    register_liquidity(
        registry
    )

    register_order_block(
        registry
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False


def test_confluence_can_raise_ready_setup_over_threshold() -> None:
    registry = make_ready_registry(
        confidence=58.0
    )

    register_structure(
        registry,
        confidence=58.0,
    )

    register_liquidity(
        registry,
        confidence=58.0,
    )

    result = evaluate(
        registry,
        minimum_ready_confidence=60.0,
    )

    assert result.confidence == 63.0
    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_no_confluence_leaves_low_confidence_as_prepare() -> None:
    registry = make_ready_registry(
        confidence=58.0
    )

    result = evaluate(
        registry,
        minimum_ready_confidence=60.0,
    )

    assert result.confidence == 58.0
    assert result.decision is DirectorDecision.PREPARE
    assert result.actionable is False