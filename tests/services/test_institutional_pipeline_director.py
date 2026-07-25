from __future__ import annotations

from datetime import datetime, timezone

from dataclasses import replace

from imie.directors.decision_director import (
    DecisionDirector,
    DecisionDirectorConfig,
)
from imie.engines.trend import (
    TrendAnalyst,
)
from imie.models import (
    AcceptanceResult,
    AnalystRegistry,
    AnalystResult,
    DataFreshness,
    MarketMeasurements,
    MarketObservations,
    MarketPhaseType,
    SetupLifecycle,
    TradePlan,
)
from imie.services import (
    build_institutional_results,
)
from imie.utils.analyst_ids import (
    ANALYST_ACCEPTANCE,
    ANALYST_AUCTION,
    ANALYST_PARTICIPATION,
    ANALYST_PRESSURE,
    ANALYST_RISK,
    ANALYST_SETUP,
    ANALYST_VALUE,
)
from imie.utils.constants import (
    LIFECYCLE_READY,
)
from tests.test_structure_analyst import (
    create_context,
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

def make_bullish_context():
    context = create_context()

    measurements = replace(
        context.measurements,
        price=105.0,
        ema9=103.0,
        previous_ema9=102.5,
        ema9_slope=0.5,
        vwap=102.0,
        atr14=1.0,
        core_tolerance=0.20,
    )

    observations = MarketObservations(
        price_above_ema9=True,
        price_below_ema9=False,
        price_above_vwap=True,
        price_below_vwap=False,
        ema9_rising=True,
        ema9_falling=False,
        within_core_zone=True,
    )

    return replace(
        context,
        measurements=measurements,
        observations=observations,
    )

def make_setup_payload() -> SetupLifecycle:
    return SetupLifecycle(
        symbol="NVDA",
        state=LIFECYCLE_READY,
        direction="long",
        confidence=90.0,
        atr_distance=0.0,
        action="Evaluate Entry",
        reason="Setup lifecycle is ready.",
    )


def make_acceptance_payload() -> AcceptanceResult:
    return AcceptanceResult(
        symbol="NVDA",
        accepted=True,
        direction="long",
        level="STRONG",
        score=90,
        confidence=90.0,
        trigger_price=100.0,
        previous_level=99.50,
        pullback_low=99.0,
        pullback_high=100.0,
        evidence=[
            "Completed-candle acceptance confirmed.",
        ],
        warnings=[],
        reason="Acceptance is confirmed.",
    )


def make_trade_plan() -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        valid=True,
        actionable=True,
        decision="READY",
        entry=100.0,
        stop=99.0,
        target1=101.0,
        target2=102.0,
        risk_per_share=1.0,
        reward1_per_share=1.0,
        reward2_per_share=2.0,
        rr1=1.0,
        rr2=2.0,
        quality=90,
        confidence=90.0,
        reasons=[
            "Risk validation passed.",
        ],
        warnings=[],
        narrative="Institutional pipeline integration fixture.",
    )


def make_execution_result(
    *,
    analyst: str,
    analyst_id: str,
    opinion: str,
    payload: object,
) -> AnalystResult:
    return AnalystResult(
        analyst=analyst,
        analyst_id=analyst_id,
        opinion=opinion,
        confidence=90.0,
        evidence=[],
        warnings=[],
        payload=payload,
        enabled=True,
    )


def test_real_pipeline_reaches_decision_director() -> None:
    context = make_bullish_context()

    trend_result = TrendAnalyst().analyze(
        context
    )

    assert trend_result.opinion == "BULLISH"

    institutional_results = (
        build_institutional_results(
            context,
            trend_result,
        )
    )

    registry = AnalystRegistry()

    registry.register(
        trend_result
    )

    for result in institutional_results:
        registry.register(
            result
        )

    setup_payload = make_setup_payload()
    acceptance_payload = make_acceptance_payload()
    trade_plan = make_trade_plan()

    registry.register(
        make_execution_result(
            analyst="SetupLifecycleAnalyst",
            analyst_id=ANALYST_SETUP,
            opinion=LIFECYCLE_READY,
            payload=setup_payload,
        )
    )

    registry.register(
        make_execution_result(
            analyst="AcceptanceAnalyst",
            analyst_id=ANALYST_ACCEPTANCE,
            opinion="STRONG",
            payload=acceptance_payload,
        )
    )

    registry.register(
        make_execution_result(
            analyst="RiskAnalyst",
            analyst_id=ANALYST_RISK,
            opinion="READY",
            payload=trade_plan,
        )
    )

    director = DecisionDirector(
        config=DecisionDirectorConfig(
            institutional_bias_policy="READY",
            market_phase_policy="ADVISORY",
        )
    )

    decision = director.evaluate(
        context=context,
        freshness=make_freshness(),
        registry=registry,
    )

    assert registry.get(
        ANALYST_AUCTION
    ) is not None

    assert registry.get(
        ANALYST_PRESSURE
    ) is not None

    assert registry.get(
        ANALYST_PARTICIPATION
    ) is not None

    assert registry.get(
        ANALYST_VALUE
    ) is not None

    assert registry.contains(
        ANALYST_AUCTION
    )
    assert registry.contains(
        ANALYST_PRESSURE
    )
    assert registry.contains(
        ANALYST_PARTICIPATION
    )
    assert registry.contains(
        ANALYST_VALUE
    )

    assert (
        ANALYST_AUCTION
        in decision.analyst_summary
    )
    assert (
        ANALYST_PRESSURE
        in decision.analyst_summary
    )
    assert (
        ANALYST_PARTICIPATION
        in decision.analyst_summary
    )
    assert (
        ANALYST_VALUE
        in decision.analyst_summary
    )

    assert (
        "Auction result is missing."
        not in decision.warnings
    )
    assert (
        "Pressure result is missing."
        not in decision.warnings
    )
    assert (
        "Participation result is missing."
        not in decision.warnings
    )
    assert (
        "Value result is missing."
        not in decision.warnings
    )

    assert (
    decision.institutional_context
    is not None
    )

    institutional_context = (
        decision.institutional_context
    )

    assert (
        institutional_context.setup_lifecycle
        is setup_payload
    )

    assert (
        institutional_context.acceptance
        is acceptance_payload
    )

    assert (
        institutional_context.risk
        is trade_plan
    )

    assert (
        institutional_context
        .institutional_bias
        .direction
        .value
        != "UNKNOWN"
    )

    assert (
        institutional_context
        .market_phase
        .phase
        is not MarketPhaseType.UNKNOWN
    )