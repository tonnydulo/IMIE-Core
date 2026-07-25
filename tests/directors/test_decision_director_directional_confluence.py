from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from imie.directors.market_phase_engine import (
    MarketPhaseEngine,
)

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
    MarketPhase,
    MarketPhaseType,
    SetupLifecycle,
    AcceptanceResult,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_AUCTION,
    ANALYST_LIQUIDITY,
    ANALYST_ORDER_BLOCK,
    ANALYST_PARTICIPATION,
    ANALYST_PRESSURE,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_STRUCTURE,
    ANALYST_TREND,
    ANALYST_VALUE,
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

class FixedMarketPhaseEngine(
    MarketPhaseEngine
):
    def __init__(
        self,
        phase: MarketPhaseType,
    ) -> None:
        super().__init__()
        self.phase = phase

    def evaluate(
        self,
        **kwargs,
    ) -> MarketPhase:
        del kwargs

        if self.phase is MarketPhaseType.UNKNOWN:
            return MarketPhase(
                phase=MarketPhaseType.UNKNOWN,
                confidence=0.0,
                strength=0.0,
                phase_scores=(),
                agreement_count=0,
                conflict_count=0,
                supporting_domains=(),
                opposing_domains=(),
                neutral_domains=(),
                unknown_domains=(
                    "STRUCTURE",
                    "AUCTION",
                    "LIQUIDITY",
                    "PRESSURE",
                    "PARTICIPATION",
                    "ORDER_BLOCK",
                    "TREND",
                    "VALUE",
                ),
                evidence=(),
                warnings=(
                    "No resolved market phase votes are available.",
                ),
            )

        return MarketPhase(
            phase=self.phase,
            confidence=90.0,
            strength=75.0,
            phase_scores=(),
            agreement_count=4,
            conflict_count=0,
            supporting_domains=(
                "STRUCTURE",
                "AUCTION",
                "TREND",
                "VALUE",
            ),
            opposing_domains=(),
            neutral_domains=(),
            unknown_domains=(),
            evidence=(
                (
                    "Fixed market phase fixture resolved "
                    f"{self.phase.value}."
                ),
            ),
            warnings=(),
        )

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

def register_extended_domain(
    registry: AnalystRegistry,
    *,
    analyst_id: str,
    analyst: str,
    opinion: str,
) -> None:
    registry.register(
        make_result(
            analyst_id=analyst_id,
            analyst=analyst,
            opinion=opinion,
        )
    )


def evaluate(
    registry: AnalystRegistry,
    *,
    minimum_ready_confidence: float = 60.0,
    institutional_bias_policy: str = "READY",
    confluence_policy: str = "ADVISORY",
    market_phase_policy: str = "ADVISORY",
    market_phase_engine: MarketPhaseEngine | None = None,
):
    director = DecisionDirector(
        config=DecisionDirectorConfig(
            minimum_ready_confidence=(
                minimum_ready_confidence
            ),
            institutional_bias_policy=(
                institutional_bias_policy
            ),
            confluence_policy=(
                confluence_policy
            ),
            market_phase_policy=(
                market_phase_policy
            ),
        ),
        market_phase_engine=market_phase_engine,
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

def add_expanded_confluence(
    registry: AnalystRegistry,
    *,
    structure: str,
    liquidity: str,
    order_block: str,
    auction: str,
    pressure: str,
    participation: str,
    value: str,
) -> None:
    register_structure(
        registry,
        structure,
    )

    register_liquidity(
        registry,
        liquidity,
    )

    register_order_block(
        registry,
        order_block,
    )

    register_extended_domain(
        registry,
        analyst_id=ANALYST_AUCTION,
        analyst="AuctionAnalyst",
        opinion=auction,
    )

    register_extended_domain(
        registry,
        analyst_id=ANALYST_PRESSURE,
        analyst="PressureAnalyst",
        opinion=pressure,
    )

    register_extended_domain(
        registry,
        analyst_id=ANALYST_PARTICIPATION,
        analyst="ParticipationAnalyst",
        opinion=participation,
    )

    register_extended_domain(
        registry,
        analyst_id=ANALYST_VALUE,
        analyst="ValueAnalyst",
        opinion=value,
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

def test_bias_policy_defaults_to_prepare() -> None:
    config = DecisionDirectorConfig()

    assert (
        config.institutional_bias_policy
        == "PREPARE"
    )


def test_bias_policy_is_normalized() -> None:
    config = DecisionDirectorConfig(
        institutional_bias_policy="pass",
    )

    assert (
        config.institutional_bias_policy
        == "PASS"
    )


def test_invalid_bias_policy_raises() -> None:
    with pytest.raises(
        ValueError,
        match="institutional_bias_policy",
    ):
        DecisionDirectorConfig(
            institutional_bias_policy="INVALID",
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

def test_opposing_bias_prepare_policy_downgrades_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BEARISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="PREPARE",
    )

    assert (
        result.decision
        is DirectorDecision.PREPARE
    )
    assert result.actionable is False
    assert result.trade_plan is not None

    assert any(
        "trade authorization was reduced"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "institutional bias is bearish"
        in reason.lower()
        for reason in result.reasons
    )


def test_opposing_bias_pass_policy_rejects_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BEARISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="PASS",
    )

    assert (
        result.decision
        is DirectorDecision.PASS
    )
    assert result.actionable is False
    assert result.trade_plan is not None

    assert (
        "opposes the dominant institutional bias"
        in result.recommendation.lower()
    )

    assert any(
        "trade authorization was reduced"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "institutional bias is bearish"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "intended trade direction is bullish"
        in reason.lower()
        for reason in result.reasons
    )


def test_opposing_bias_ready_policy_remains_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BEARISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True
    assert result.trade_plan is not None

    assert any(
        "institutional bias alignment is opposed"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "institutional bias opposes"
        in warning.lower()
        for warning in result.warnings
    )


def test_aligned_bias_remains_ready_under_prepare_policy() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="PREPARE",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True
    assert result.trade_plan is not None

    assert any(
        "institutional bias alignment is aligned"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "institutional bias aligns with the intended bullish trade"
        in reason.lower()
        for reason in result.reasons
    )

def test_unknown_market_phase_is_reported() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert (
        "Market phase is UNKNOWN."
        in result.reasons
    )

    assert (
        "Market phase confidence is 0%."
        in result.reasons
    )

    assert (
        "Market phase strength is 0."
        in result.reasons
    )

def test_unknown_market_phase_warning_is_reported() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
    )

    assert (
        "No resolved market phase votes are available."
        in result.warnings
    )

def test_market_phase_is_advisory_only() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True
    assert result.trade_plan is not None

    assert (
        "Market phase agreement count is 0."
        in result.reasons
    )

    assert (
        "Market phase conflict count is 0."
        in result.reasons
    )

def test_market_phase_policy_defaults_to_advisory() -> None:
    config = DecisionDirectorConfig()

    assert (
        config.market_phase_policy
        == "ADVISORY"
    )


def test_market_phase_policy_is_normalized() -> None:
    config = DecisionDirectorConfig(
        market_phase_policy="prepare",
    )

    assert (
        config.market_phase_policy
        == "PREPARE"
    )


def test_invalid_market_phase_policy_raises() -> None:
    with pytest.raises(
        ValueError,
        match="market_phase_policy",
    ):
        DecisionDirectorConfig(
            market_phase_policy="INVALID",
        )

def test_opposed_phase_prepare_policy_downgrades_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="PREPARE",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.MARKDOWN
        ),
    )

    assert (
        result.decision
        is DirectorDecision.PREPARE
    )
    assert result.actionable is False
    assert result.trade_plan is not None

    assert any(
        "market phase opposes"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "market phase is markdown"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "market phase policy is prepare"
        in reason.lower()
        for reason in result.reasons
    )

def test_opposed_phase_pass_policy_rejects_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="PASS",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.MARKDOWN
        ),
    )

    assert (
        result.decision
        is DirectorDecision.PASS
    )
    assert result.actionable is False
    assert result.trade_plan is not None

    assert (
        "market phase opposes the intended trade direction"
        in result.recommendation.lower()
    )

    assert any(
        "trade authorization was rejected"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "market phase policy is pass"
        in reason.lower()
        for reason in result.reasons
    )

def test_unknown_phase_prepare_policy_downgrades_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="PREPARE",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.UNKNOWN
        ),
    )

    assert (
        result.decision
        is DirectorDecision.PREPARE
    )
    assert result.actionable is False

    assert any(
        "market phase compatibility is unresolved"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "unresolved or transitional market phase"
        in warning.lower()
        for warning in result.warnings
    )

def test_unknown_phase_pass_policy_still_prepares() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="PASS",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.UNKNOWN
        ),
    )

    assert (
        result.decision
        is DirectorDecision.PREPARE
    )
    assert result.actionable is False

    assert any(
        "market phase policy is pass"
        in reason.lower()
        for reason in result.reasons
    )

def test_opposed_phase_advisory_policy_remains_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="ADVISORY",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.MARKDOWN
        ),
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert any(
        "market phase opposes the intended bullish trade"
        in warning.lower()
        for warning in result.warnings
    )

def test_aligned_phase_remains_ready_under_prepare_policy() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="PREPARE",
        market_phase_engine=FixedMarketPhaseEngine(
            MarketPhaseType.MARKUP
        ),
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert any(
        "market phase aligns with the intended bullish trade"
        in reason.lower()
        for reason in result.reasons
    )

def test_typed_payloads_attach_institutional_context() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    setup_payload = SetupLifecycle(
        symbol="SPY",
        state=LIFECYCLE_READY,
        direction="long",
        confidence=90.0,
        atr_distance=0.0,
        action="Evaluate Entry",
        reason="Setup lifecycle is ready.",
    )

    acceptance_payload = AcceptanceResult(
        symbol="SPY",
        accepted=True,
        direction="long",
        level="STRONG",
        score=90,
        confidence=90.0,
        trigger_price=500.0,
        previous_level=499.5,
        pullback_low=499.0,
        pullback_high=500.0,
        evidence=[
            "Completed-candle acceptance confirmed.",
        ],
        warnings=[],
        reason="Acceptance is confirmed.",
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_SETUP,
            analyst="SetupLifecycleAnalyst",
            opinion=LIFECYCLE_READY,
            confidence=90.0,
            payload=setup_payload,
        )
    )

    registry.register(
        make_result(
            analyst_id=ANALYST_ACCEPTANCE,
            analyst="AcceptanceAnalyst",
            opinion="STRONG",
            confidence=90.0,
            payload=acceptance_payload,
        )
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="ADVISORY",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert result.institutional_context is not None

    context = result.institutional_context

    assert (
        context.setup_lifecycle
        is setup_payload
    )
    assert (
        context.acceptance
        is acceptance_payload
    )
    assert (
        context.risk
        is result.trade_plan
    )
    assert (
        context.trend
        is registry.get(ANALYST_TREND)
    )
    assert (
        context.institutional_bias.direction.value
        == "BULLISH"
    )
    assert (
        context.institutional_confluence
        is not None
    )
    assert (
        context.market_phase
        is not None
    )


def test_lightweight_payloads_leave_institutional_context_none() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        market_phase_policy="ADVISORY",
    )

    assert (
        result.decision
        is DirectorDecision.READY
    )
    assert result.actionable is True

    assert result.institutional_context is None


def test_confluence_policy_defaults_to_advisory() -> None:
    config = DecisionDirectorConfig()

    assert config.confluence_policy == "ADVISORY"


def test_confluence_policy_is_normalized() -> None:
    config = DecisionDirectorConfig(
        confluence_policy="prepare",
    )

    assert config.confluence_policy == "PREPARE"


def test_invalid_confluence_policy_raises() -> None:
    with pytest.raises(
        ValueError,
        match="confluence_policy",
    ):
        DecisionDirectorConfig(
            confluence_policy="INVALID",
        )

def test_opposing_confluence_prepare_policy_downgrades_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PREPARE",
    )

    assert result.decision is DirectorDecision.PREPARE
    assert result.actionable is False
    assert result.trade_plan is not None

    assert any(
        "confluence opposes"
        in reason.lower()
        for reason in result.reasons
    )


def test_opposing_confluence_advisory_remains_ready() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="ADVISORY",
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_strong_opposing_confluence_pass_policy_rejects() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bearish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PASS",
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False

    assert (
        "strong institutional confluence opposes"
        in result.recommendation.lower()
    )


def test_aligned_confluence_remains_ready_under_prepare_policy() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_all_bullish(
        registry
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PREPARE",
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_unknown_confluence_does_not_downgrade_prepare_policy() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PREPARE",
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True


def test_value_opposition_alone_does_not_downgrade() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_expanded_confluence(
        registry,
        structure="BULLISH",
        liquidity="BULLISH",
        order_block="BULLISH",
        auction="BULLISH",
        pressure="BULLISH",
        participation="BULLISH",
        value="BEARISH",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PASS",
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True

    assert result.institutional_context is None

    assert any(
        "institutional conflict is present"
        in warning.lower()
        for warning in result.warnings
    )

def test_single_auction_vote_does_not_defeat_broad_opposition() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_expanded_confluence(
        registry,
        structure="BEARISH",
        liquidity="BEARISH",
        order_block="BEARISH",
        auction="BULLISH",
        pressure="BEARISH",
        participation="BEARISH",
        value="BEARISH",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PASS",
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False

    assert any(
        "confluence policy is pass"
        in reason.lower()
        for reason in result.reasons
    )

def test_four_domain_strong_opposition_triggers_pass() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_expanded_confluence(
        registry,
        structure="BEARISH",
        liquidity="BEARISH",
        order_block="BEARISH",
        auction="BEARISH",
        pressure="BULLISH",
        participation="NEUTRAL",
        value="NEUTRAL",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PASS",
    )

    assert result.decision is DirectorDecision.PASS
    assert result.actionable is False

    assert any(
        "institutional agreement count is 4"
        in reason.lower()
        for reason in result.reasons
    )

def test_mixed_weak_opposition_pass_policy_prepares() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
    )

    add_expanded_confluence(
        registry,
        structure="BEARISH",
        liquidity="BEARISH",
        order_block="BULLISH",
        auction="BEARISH",
        pressure="NEUTRAL",
        participation="UNKNOWN",
        value="NEUTRAL",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PASS",
    )

    assert result.decision is DirectorDecision.PREPARE
    assert result.actionable is False

    assert any(
        "confluence policy is pass"
        in reason.lower()
        for reason in result.reasons
    )

def test_fully_aligned_expanded_confluence_adds_eight() -> None:
    registry = make_ready_registry(
        trend=TREND_BULLISH,
        plan_direction="long",
        confidence=90.0,
    )

    add_expanded_confluence(
        registry,
        structure="BULLISH",
        liquidity="BULLISH",
        order_block="BULLISH",
        auction="BULLISH",
        pressure="BULLISH",
        participation="BULLISH",
        value="BULLISH",
    )

    result = evaluate(
        registry,
        institutional_bias_policy="READY",
        confluence_policy="PREPARE",
    )

    assert result.decision is DirectorDecision.READY
    assert result.actionable is True
    assert result.confidence == 98.0

    assert any(
        "available institutional confidence adjustment is +8"
        in reason.lower()
        for reason in result.reasons
    )

    assert any(
        "applied institutional confidence adjustment is +8"
        in reason.lower()
        for reason in result.reasons
    )


