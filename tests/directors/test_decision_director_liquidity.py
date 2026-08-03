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
    ANALYST_LIQUIDITY,
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
    Minimal acceptance payload for Director testing.
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
                "Risk analysis produced an actionable TradePlan.",
            ],
            payload=make_trade_plan(),
        )
    )

    return registry


def register_liquidity(
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
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
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


def test_liquidity_is_not_a_core_required_analyst() -> None:
    assert (
        ANALYST_LIQUIDITY
        not in CORE_ANALYST_IDS
    )


def test_missing_liquidity_does_not_prevent_ready() -> None:
    registry = make_ready_registry()

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True
    assert (
        ANALYST_LIQUIDITY
        not in result.analyst_summary
    )


def test_missing_liquidity_is_not_reported_as_missing() -> None:
    registry = AnalystRegistry()
    director = DecisionDirector()

    result = director.evaluate(
        context=None,  # type: ignore[arg-type]
        freshness=make_freshness(),
        registry=registry,
    )

    assert result.decision is DirectorDecision.WAIT

    assert all(
        ANALYST_LIQUIDITY not in reason
        for reason in result.reasons
    )


def test_enabled_liquidity_appears_in_summary() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        ANALYST_LIQUIDITY
        in result.analyst_summary
    )

    assert (
        result.analyst_summary[
            ANALYST_LIQUIDITY
        ]["enabled"]
        is True
    )


def test_disabled_liquidity_support_returns_empty() -> None:
    director = DecisionDirector()

    liquidity = make_result(
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        enabled=False,
    )

    evidence, warnings = (
        director._liquidity_support(
            liquidity
        )
    )

    assert evidence == ()
    assert warnings == ()


def test_disabled_liquidity_does_not_block_ready() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity supply remains active."
        ),
        enabled=False,
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True

    assert (
        "Institutional liquidity supply is nearby."
        not in result.warnings
    )


def test_demand_adds_liquidity_opinion_to_reasons() -> None:
    registry = make_ready_registry()

    opinion = (
        "Institutional liquidity demand remains active."
    )

    register_liquidity(
        registry,
        opinion=opinion,
    )

    result = evaluate(
        registry
    )

    assert (
        f"Liquidity Analyst: {opinion}."
        in result.reasons
    )


def test_demand_adds_supporting_evidence() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional liquidity demand supports the setup."
        in result.reasons
    )


def test_demand_does_not_add_supply_warning() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional liquidity supply is nearby."
        not in result.warnings
    )


def test_supply_adds_warning() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity supply remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert (
        "Institutional liquidity supply is nearby."
        in result.warnings
    )


def test_supply_does_not_block_ready() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity supply remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_supply_adds_liquidity_opinion_to_reasons() -> None:
    registry = make_ready_registry()

    opinion = (
        "Institutional liquidity supply remains active."
    )

    register_liquidity(
        registry,
        opinion=opinion,
    )

    result = evaluate(
        registry
    )

    assert (
        f"Liquidity Analyst: {opinion}."
        in result.reasons
    )


@pytest.mark.parametrize(
    "opinion",
    [
        "institutional liquidity demand remains active",
        "Institutional Liquidity Demand Remains Active",
        "INSTITUTIONAL LIQUIDITY DEMAND REMAINS ACTIVE",
    ],
)
def test_demand_opinion_is_case_insensitive(
    opinion: str,
) -> None:
    director = DecisionDirector()

    liquidity = make_result(
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._liquidity_support(
            liquidity
        )
    )

    assert (
        "Institutional liquidity demand supports the setup."
        in evidence
    )

    assert warnings == ()


@pytest.mark.parametrize(
    "opinion",
    [
        "institutional liquidity supply remains active",
        "Institutional Liquidity Supply Remains Active",
        "INSTITUTIONAL LIQUIDITY SUPPLY REMAINS ACTIVE",
    ],
)
def test_supply_opinion_is_case_insensitive(
    opinion: str,
) -> None:
    director = DecisionDirector()

    liquidity = make_result(
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._liquidity_support(
            liquidity
        )
    )

    assert evidence

    assert warnings == (
        "Institutional liquidity supply is nearby.",
    )


def test_buy_side_liquidity_is_preserved_as_context() -> None:
    director = DecisionDirector()

    opinion = (
        "Institutional buy-side liquidity remains active."
    )

    liquidity = make_result(
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._liquidity_support(
            liquidity
        )
    )

    assert evidence == (
        f"Liquidity Analyst: {opinion}.",
    )

    assert warnings == ()


def test_sell_side_liquidity_is_preserved_as_context() -> None:
    director = DecisionDirector()

    opinion = (
        "Institutional sell-side liquidity remains active."
    )

    liquidity = make_result(
        analyst_id=ANALYST_LIQUIDITY,
        analyst="LiquidityAnalyst",
        opinion=opinion,
    )

    evidence, warnings = (
        director._liquidity_support(
            liquidity
        )
    )

    assert evidence == (
        f"Liquidity Analyst: {opinion}.",
    )

    assert warnings == ()


def test_balanced_liquidity_is_non_blocking() -> None:
    registry = make_ready_registry()

    opinion = (
        "Institutional liquidity remains balanced."
    )

    register_liquidity(
        registry,
        opinion=opinion,
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True

    assert (
        f"Liquidity Analyst: {opinion}."
        in result.reasons
    )


def test_unknown_liquidity_opinion_is_non_blocking() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion="Liquidity context unavailable.",
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True

    assert (
        "Institutional liquidity supply is nearby."
        not in result.warnings
    )

    assert (
        "Institutional liquidity demand supports the setup."
        not in result.reasons
    )


def test_arbitrary_payload_is_ignored() -> None:
    registry = make_ready_registry()

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        payload=object(),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.READY

    assert (
        "Institutional liquidity demand supports the setup."
        in result.reasons
    )


def test_liquidity_evidence_is_collected_once() -> None:
    registry = make_ready_registry()

    duplicate = (
        "One active liquidity pool identified."
    )

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
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


def test_liquidity_warning_is_collected_once() -> None:
    registry = make_ready_registry()

    warning = (
        "Institutional liquidity supply is nearby."
    )

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity supply remains active."
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


def test_liquidity_does_not_override_neutral_trend() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_TREND,
            analyst="Trend Analyst",
            opinion=TREND_NEUTRAL,
        )
    )

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.IGNORE
    assert result.actionable is False


def test_liquidity_does_not_override_waiting_setup() -> None:
    registry = make_ready_registry()

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="Setup Analyst",
            opinion=LIFECYCLE_EXTENDED,
        )
    )

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_liquidity_does_not_override_failed_acceptance() -> None:
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

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.WAIT
    assert result.actionable is False


def test_liquidity_does_not_override_invalid_trade_plan() -> None:
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

    register_liquidity(
        registry,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
    )

    result = evaluate(
        registry
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False


def test_liquidity_support_adds_confluence_adjustment() -> None:
    registry_without = make_ready_registry()

    result_without = evaluate(
        registry_without
    )

    registry_with = make_ready_registry()

    register_liquidity(
        registry_with,
        opinion=(
            "Institutional liquidity demand remains active."
        ),
        confidence=90.0,
    )

    result_with = evaluate(
        registry_with
    )

    assert result_without.confidence == 90.0
    assert result_with.confidence == 92.0

    assert (
        result_with.confidence
        == result_without.confidence + 2.0
    )

    assert (
        "Institutional confidence adjustment is +2."
        in result_with.reasons
    )