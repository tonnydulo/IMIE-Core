from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from imie.directors.decision_director import (
    DecisionDirector,
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
    ANALYST_ORDER_BLOCK,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_TREND,
    CORE_ANALYST_IDS,
)
from imie.utils.constants import (
    LIFECYCLE_EXTENDED,
    LIFECYCLE_READY,
    TREND_BULLISH,
    TREND_NEUTRAL,
)


class AcceptancePayload:
    """
    Minimal payload used by DecisionDirector acceptance checks.
    """

    def __init__(
        self,
        accepted: bool,
    ) -> None:
        self.accepted = accepted


def make_freshness(
    *,
    actionable: bool = True,
    reason: str = "",
) -> DataFreshness:
    now = datetime.now(
        timezone.utc
    )

    return DataFreshness(
        status=(
            "FRESH"
            if actionable
            else "STALE"
        ),
        actionable=actionable,
        checked_at=now,
        quote_timestamp=now,
        latest_bar_timestamp=now,
        quote_age_seconds=0.0,
        bar_age_seconds=0.0,
        quote_bar_gap_seconds=0.0,
        quote_is_fresh=actionable,
        bar_is_fresh=actionable,
        timestamps_aligned=actionable,
        reason=reason,
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
                "Projected reward-to-risk failed validation.",
            ]
        ),
        narrative=(
            "A valid Pullback-to-Core TradePlan is available."
            if valid
            else "The proposed TradePlan is invalid."
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


def make_ready_registry() -> AnalystRegistry:
    registry = AnalystRegistry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            opinion=TREND_BULLISH,
            evidence=[
                "Bullish trend confirmed.",
            ],
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            opinion=LIFECYCLE_READY,
            evidence=[
                "Setup lifecycle is READY.",
            ],
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            opinion="STRONG",
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
            analyst="Risk Analyst",
            opinion="READY",
            evidence=[
                (
                    "Risk analysis produced an actionable "
                    "TradePlan."
                ),
            ],
            payload=make_trade_plan(),
        )
    )

    return registry


def register_order_block(
    registry: AnalystRegistry,
    *,
    opinion: str,
    confidence: float = 90.0,
    enabled: bool = True,
    evidence: list[str] | None = None,
    warnings: list[str] | None = None,
    payload: Any | None = None,
) -> AnalystResult:
    result = make_result(
        analyst_id=ANALYST_ORDER_BLOCK,
        analyst="OrderBlockAnalyst",
        opinion=opinion,
        confidence=confidence,
        enabled=enabled,
        evidence=evidence,
        warnings=warnings,
        payload=payload,
    )

    registry.register(
        result
    )

    return result


def evaluate(
    registry: AnalystRegistry,
):
    director = DecisionDirector()

    return director.evaluate(
        context=None,  # type: ignore[arg-type]
        freshness=make_freshness(),
        registry=registry,
    )


def test_order_block_is_not_a_core_required_analyst() -> None:
    assert (
        ANALYST_ORDER_BLOCK
        not in CORE_ANALYST_IDS
    )


def test_missing_order_block_does_not_prevent_ready() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True
    assert (
        ANALYST_ORDER_BLOCK
        not in result.analyst_summary
    )


def test_missing_order_block_is_not_reported_as_missing() -> None:
    registry = AnalystRegistry()
    director = DecisionDirector()

    result = director.evaluate(
        context=None,  # type: ignore[arg-type]
        freshness=make_freshness(),
        registry=registry,
    )

    assert result.decision is DirectorDecision.WAIT
    assert all(
        ANALYST_ORDER_BLOCK not in reason
        for reason in result.reasons
    )


def test_enabled_order_block_appears_in_summary() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        ANALYST_ORDER_BLOCK
        in result.analyst_summary
    )
    assert (
        result.analyst_summary[
            ANALYST_ORDER_BLOCK
        ]["enabled"]
        is True
    )


def test_disabled_order_block_is_ignored_by_support_helper() -> None:
    director = DecisionDirector()

    result = make_result(
        analyst_id=ANALYST_ORDER_BLOCK,
        analyst="OrderBlockAnalyst",
        opinion=(
            "Active institutional demand remains below price."
        ),
        enabled=False,
    )

    evidence, warnings = (
        director._order_block_support(
            result
        )
    )

    assert evidence == ()
    assert warnings == ()


def test_disabled_order_block_does_not_block_ready() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional supply remains above price."
        ),
        enabled=False,
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True
    assert (
        "Institutional supply is nearby."
        not in result.warnings
    )


def test_demand_adds_order_block_opinion_to_reasons() -> None:
    registry = make_ready_registry()

    opinion = (
        "Active institutional demand remains below price."
    )

    register_order_block(
        registry,
        opinion=opinion,
    )

    result = evaluate(
        registry
    )

    assert (
        f"Order Block Analyst: {opinion}."
        in result.reasons
    )


def test_demand_adds_supporting_evidence() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional demand supports the setup."
        in result.reasons
    )


def test_demand_does_not_add_supply_warning() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional supply is nearby."
        not in result.warnings
    )


def test_supply_adds_warning() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional supply remains above price."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional supply is nearby."
        in result.warnings
    )


def test_supply_does_not_block_ready() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional supply remains above price."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_supply_adds_order_block_opinion_to_reasons() -> None:
    registry = make_ready_registry()

    opinion = (
        "Active institutional supply remains above price."
    )

    register_order_block(
        registry,
        opinion=opinion,
    )

    result = evaluate(
        registry
    )

    assert (
        f"Order Block Analyst: {opinion}."
        in result.reasons
    )


@pytest.mark.parametrize(
    "opinion",
    [
        (
            "active institutional demand remains "
            "below price"
        ),
        (
            "Active Institutional Demand Remains "
            "Below Price"
        ),
        (
            "ACTIVE INSTITUTIONAL DEMAND REMAINS "
            "BELOW PRICE"
        ),
    ],
)
def test_demand_opinion_is_case_insensitive(
    opinion: str,
) -> None:
    director = DecisionDirector()

    order_block = make_result(
        analyst_id=ANALYST_ORDER_BLOCK,
        analyst="OrderBlockAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._order_block_support(
            order_block
        )
    )

    assert (
        "Institutional demand supports the setup."
        in evidence
    )
    assert warnings == ()


@pytest.mark.parametrize(
    "opinion",
    [
        (
            "active institutional supply remains "
            "above price"
        ),
        (
            "Active Institutional Supply Remains "
            "Above Price"
        ),
        (
            "ACTIVE INSTITUTIONAL SUPPLY REMAINS "
            "ABOVE PRICE"
        ),
    ],
)
def test_supply_opinion_is_case_insensitive(
    opinion: str,
) -> None:
    director = DecisionDirector()

    order_block = make_result(
        analyst_id=ANALYST_ORDER_BLOCK,
        analyst="OrderBlockAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._order_block_support(
            order_block
        )
    )

    assert evidence
    assert warnings == (
        "Institutional supply is nearby.",
    )


def test_balanced_order_block_adds_no_directional_support() -> None:
    director = DecisionDirector()

    opinion = (
        "Institutional order flow remains balanced."
    )

    order_block = make_result(
        analyst_id=ANALYST_ORDER_BLOCK,
        analyst="OrderBlockAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._order_block_support(
            order_block
        )
    )

    assert evidence == (
        f"Order Block Analyst: {opinion}.",
    )
    assert warnings == ()


def test_unknown_order_block_opinion_is_non_blocking() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion="Order block context unavailable.",
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True
    assert (
        "Institutional supply is nearby."
        not in result.warnings
    )
    assert (
        "Institutional demand supports the setup."
        not in result.reasons
    )


def test_arbitrary_payload_is_ignored() -> None:
    registry = make_ready_registry()

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
        payload=object(),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert (
        "Institutional demand supports the setup."
        in result.reasons
    )


def test_order_block_evidence_is_collected_once() -> None:
    registry = make_ready_registry()

    duplicate = (
        "Fresh bullish order block detected."
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
        evidence=[
            duplicate,
            duplicate,
        ],
    )

    result = evaluate(
        registry
    )

    assert result.reasons.count(
        duplicate
    ) == 1


def test_order_block_warning_is_collected_once() -> None:
    registry = make_ready_registry()

    warning = (
        "Institutional supply is nearby."
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional supply remains above price."
        ),
        warnings=[
            warning,
            warning,
        ],
    )

    result = evaluate(
        registry
    )

    assert result.warnings.count(
        warning
    ) == 1


def test_order_block_does_not_override_neutral_trend() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            opinion=TREND_NEUTRAL,
        )
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.IGNORE
    assert result.actionable is False


def test_order_block_does_not_override_waiting_setup() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            opinion=LIFECYCLE_EXTENDED,
        )
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_order_block_does_not_override_failed_acceptance() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="Acceptance Analyst",
            opinion="NONE",
            confidence=0.0,
            payload=AcceptancePayload(
                accepted=False
            ),
        )
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_order_block_does_not_override_invalid_trade_plan() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_RISK,
            analyst="Risk Analyst",
            opinion="PASS",
            confidence=0.0,
            payload=make_trade_plan(
                valid=False,
                actionable=False,
            ),
        )
    )

    register_order_block(
        registry,
        opinion=(
            "Active institutional demand remains below price."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False


def test_order_block_support_adds_confluence_adjustment() -> None:
    registry_without = make_ready_registry()

    without_order_block = evaluate(
        registry_without
    )

    registry_with = make_ready_registry()

    register_order_block(
        registry_with,
        opinion=(
            "Active institutional demand remains below price."
        ),
        confidence=90.0,
    )

    with_order_block = evaluate(
        registry_with
    )

    assert without_order_block.confidence == 90.0
    assert with_order_block.confidence == 92.0
    assert (
        with_order_block.confidence
        == without_order_block.confidence + 2.0
    )

    assert (
        "Institutional confidence adjustment is +2."
        in with_order_block.reasons
    )