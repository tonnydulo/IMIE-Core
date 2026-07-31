import json

import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
from time import sleep

from pathlib import Path

import pytest

from zoneinfo import ZoneInfo

from imie.models import (
    AcceptanceResult,
    AnalystResult,
    DecisionResult,
    DirectorDecision,
    InstitutionalBias,
    InstitutionalConfluence,
    InstitutionalDecisionContext,
    InstitutionalDirection,
    MarketPhase,
    MarketPhaseType,
    SetupLifecycle,
    TradePlan,
)

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    DashboardStatusFilePublisher,
    MarketSessionResult,
    MarketSessionState,
    RuntimeHealthState,
    RuntimeHealthSummary,
    SessionPolicyAction,
    SessionPolicyResult,
)


NOW = datetime(
    2026,
    7,
    23,
    15,
    0,
    tzinfo=timezone.utc,
)

DEFAULT_SESSION_STATE = next(
    state
    for state in MarketSessionState
    if state is not MarketSessionState.CLOSED
)


def make_health(
    *,
    cycle_count: int = 0,
) -> RuntimeHealthSummary:
    return RuntimeHealthSummary(
        state=RuntimeHealthState.RUNNING,
        started_at=NOW,
        checked_at=NOW,
        uptime_seconds=0.0,
        last_transition_at=NOW,
        last_heartbeat_at=None,
        last_successful_cycle_at=None,
        completed_cycle_count=cycle_count,
        error_type=None,
    )


def make_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus
            .SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=(
            NOW
            + timedelta(
                seconds=2,
            )
        ),
        message="No new completed bar.",
    )

def make_market_session(
    state: MarketSessionState = (
        DEFAULT_SESSION_STATE
    ),
) -> MarketSessionResult:
    return MarketSessionResult(
        state=state,
        checked_at=NOW,
        market_time=NOW.astimezone(
            ZoneInfo(
                "America/New_York"
            )
        ),
        is_trading_day=True,
        reason="Market session evaluated.",
    )

def make_decision(
    decision: DirectorDecision = (
        DirectorDecision.PREPARE
    ),
    *,
    trade_plan: TradePlan | None = None,
    institutional_context: (
        InstitutionalDecisionContext | None
    ) = None,
) -> DecisionResult:
    actionable = (
        decision
        is DirectorDecision.READY
    )

    return DecisionResult(
        decision=decision,
        actionable=actionable,
        confidence=90.0,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        reasons=(
            "Dashboard publisher test decision.",
        ),
        warnings=(),
        analyst_summary={
        "TREND": {
            "opinion": (
                "Directional trend is bullish."
            ),
            "confidence": 82.0,
            "enabled": True,
        },
        "STRUCTURE": {
            "opinion": (
                "Bullish structure continuation "
                "is confirmed."
            ),
            "confidence": 84.0,
            "enabled": True,
        },
        "LIQUIDITY": {
            "opinion": (
                "Sell-side liquidity remains active."
            ),
            "confidence": 78.0,
            "enabled": True,
        },
        "ORDER_BLOCK": {
            "opinion": (
                "Bullish order block remains valid."
            ),
            "confidence": 81.0,
            "enabled": True,
        },
        "AUCTION": {
            "opinion": (
                "Buyers maintain auction control."
            ),
            "confidence": 79.0,
            "enabled": True,
        },
        "PRESSURE": {
            "opinion": (
                "Buying pressure remains dominant."
            ),
            "confidence": 77.0,
            "enabled": True,
        },
        "PARTICIPATION": {
            "opinion": (
                "Institutional participation is expanding."
            ),
            "confidence": 76.0,
            "enabled": True,
        },
        "VALUE": {
            "opinion": (
                "Price remains within fair value."
            ),
            "confidence": 74.0,
            "enabled": True,
        },
    },
        trade_plan=trade_plan,
        institutional_context=(
        institutional_context
    ),
    )

def make_decision_with_analyst_summary(
    analyst_summary: dict[str, dict[str, object]],
) -> DecisionResult:
    decision = make_decision()

    return DecisionResult(
        decision=decision.decision,
        actionable=decision.actionable,
        confidence=decision.confidence,
        recommendation=decision.recommendation,
        reasons=decision.reasons,
        warnings=decision.warnings,
        analyst_summary=analyst_summary,
        trade_plan=decision.trade_plan,
        institutional_context=(
            decision.institutional_context
        ),
    )

def make_completed_result_with_analyst_summary(
    analyst_summary: dict[str, dict[str, object]],
) -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=(
            NOW
            + timedelta(
                seconds=2
            )
        ),
        message="Analysis cycle completed.",
        market_session=make_market_session(),
        decision=(
            make_decision_with_analyst_summary(
                analyst_summary
            )
        ),
    )

def make_trade_plan() -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        strategy="PULLBACK_TO_CORE",
        direction="long",
        valid=True,
        actionable=True,
        decision="READY",
        entry=500.00,
        stop=499.00,
        target1=501.00,
        target2=502.00,
        risk_per_share=1.00,
        reward1_per_share=1.00,
        reward2_per_share=2.00,
        rr1=1.00,
        rr2=2.00,
        quality=90,
        confidence=90.0,
        reasons=(
            "Risk validation passed.",
        ),
        warnings=(),
        narrative=(
            "The proposed TradePlan is valid."
        ),
    )

def make_completed_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=(
            NOW
            + timedelta(
                seconds=2
            )
        ),
        message="Analysis cycle completed.",
        market_session=make_market_session(),
        decision=make_decision(),
    )

def make_completed_result_with_trade_plan() -> (
    AnalysisCycleResult
):
    trade_plan = make_trade_plan()

    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=(
            NOW
            + timedelta(
                seconds=2
            )
        ),
        message="Analysis cycle completed.",
        market_session=make_market_session(),
        decision=make_decision(
            decision=DirectorDecision.READY,
            trade_plan=trade_plan,
            institutional_context=(
                make_institutional_context(
                    trade_plan
                )
            ),
        ),
    )

def make_institutional_bias() -> InstitutionalBias:
    return InstitutionalBias(
        direction=InstitutionalDirection.BULLISH,
        strength=80.0,
        confidence=88.0,
        bullish_score=90.0,
        bearish_score=10.0,
        agreement_count=3,
        conflict_count=1,
        supporting_domains=(
            "STRUCTURE",
            "LIQUIDITY",
            "TREND",
        ),
        opposing_domains=(
            "VALUE",
        ),
        neutral_domains=(),
        unknown_domains=(),
        evidence=(
            "Institutional bias is bullish.",
        ),
        warnings=(),
    )

def make_market_phase() -> MarketPhase:
    return MarketPhase(
        phase=MarketPhaseType.MARKUP,
        confidence=84.0,
        strength=80.0,
        phase_scores=(),
        agreement_count=5,
        conflict_count=1,
        supporting_domains=(
            "STRUCTURE",
            "AUCTION",
            "TREND",
        ),
        opposing_domains=(
            "VALUE",
        ),
        neutral_domains=(),
        unknown_domains=(),
        evidence=(
            "Dominant market phase is markup.",
        ),
        warnings=(),
    )

def make_institutional_confluence() -> (
    InstitutionalConfluence
):
    return InstitutionalConfluence(
        score=100.0,
        structure_support=True,
        liquidity_support=True,
        order_block_support=True,
        agreement_count=3,
        confidence_adjustment=8.0,
        dominant_direction=(
            InstitutionalDirection.BULLISH
        ),
        bullish_count=3,
        bearish_count=0,
        neutral_count=0,
        unknown_count=0,
        conflict_count=0,
        evidence=(
            "Institutional confluence is bullish.",
        ),
        warnings=(),
    )

def make_trend_result() -> AnalystResult:
    return AnalystResult(
        analyst_id="trend",
        analyst="TrendAnalyst",
        opinion="BULLISH",
        confidence=90.0,
        enabled=True,
        evidence=(
            "Price is above EMA9 and VWAP.",
        ),
        warnings=(),
        payload=None,
    )


def make_setup_lifecycle() -> SetupLifecycle:
    return SetupLifecycle(
        symbol="NVDA",
        state="READY",
        direction="long",
        confidence=90.0,
        atr_distance=0.10,
        action="EVALUATE_ENTRY",
        reason="Setup lifecycle is ready.",
    )


def make_acceptance_result() -> AcceptanceResult:
    return AcceptanceResult(
        symbol="NVDA",
        accepted=True,
        direction="long",
        level="STRONG",
        score=90,
        confidence=90.0,
        trigger_price=500.0,
        previous_level=499.75,
        pullback_low=499.0,
        pullback_high=500.0,
        evidence=[
            "Completed-candle acceptance confirmed.",
        ],
        warnings=[],
        reason="Acceptance confirmed.",
    )

def make_institutional_context(
    trade_plan: TradePlan,
) -> InstitutionalDecisionContext:
    return InstitutionalDecisionContext(
        institutional_bias=(
            make_institutional_bias()
        ),
        institutional_confluence=(
            make_institutional_confluence()
        ),
        market_phase=(
            make_market_phase()
        ),
        trend=make_trend_result(),
        setup_lifecycle=make_setup_lifecycle(),
        acceptance=make_acceptance_result(),
        risk=trade_plan,
    )

def make_windows_permission_error(
    *,
    winerror: int,
    message: str = "Destination is temporarily locked.",
) -> PermissionError:
    error = PermissionError(
        message
    )
    error.winerror = winerror

    return error


def test_publish_result_populates_decision_details(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        make_completed_result()
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["decision_confidence"]
        == 90.0
    )

    assert (
        payload["decision_actionable"]
        is False
    )

    assert (
        payload["decision_recommendation"]
        == (
            "Prepare for a possible "
            "validated setup."
        )
    )

    assert (
        payload["trade_direction"]
        is None
    )

    assert payload["decision_reasons"] == [
        "Dashboard publisher test decision.",
    ]

    assert payload["decision_warnings"] == []


def test_health_update_creates_dashboard_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish(
        make_health()
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["state"] == "RUNNING"
    assert payload["symbol"] == "NVDA"
    assert payload["timeframe"] == "2m"
    assert payload["latest_cycle_status"] is None
    assert payload["has_cycle"] is False
    assert payload["decision_reasons"] == []
    assert payload["decision_warnings"] == []
    assert payload["analyst_summary"] == {}
    assert payload["structure_analyst"] is None
    assert payload["structure_opinion"] is None
    assert payload["structure_confidence"] is None
    assert payload["structure_enabled"] is None

    assert payload["liquidity_analyst"] is None
    assert payload["liquidity_opinion"] is None
    assert payload["liquidity_confidence"] is None
    assert payload["liquidity_enabled"] is None

    assert payload["order_block_analyst"] is None
    assert payload["order_block_opinion"] is None
    assert payload["order_block_confidence"] is None
    assert payload["order_block_enabled"] is None

    assert payload["order_block_analyst"] is None
    assert payload["order_block_opinion"] is None
    assert payload["order_block_confidence"] is None
    assert payload["order_block_enabled"] is None

    assert payload["auction_analyst"] is None
    assert payload["auction_opinion"] is None
    assert payload["auction_confidence"] is None
    assert payload["auction_enabled"] is None

    assert payload["pressure_analyst"] is None
    assert payload["pressure_opinion"] is None
    assert payload["pressure_confidence"] is None
    assert payload["pressure_enabled"] is None

    assert payload["participation_analyst"] is None
    assert payload["participation_opinion"] is None
    assert payload["participation_confidence"] is None
    assert payload["participation_enabled"] is None

    assert payload["value_analyst"] is None
    assert payload["value_opinion"] is None
    assert payload["value_confidence"] is None
    assert payload["value_enabled"] is None

    assert payload["analyst_domain_count"] == 0
    assert payload["analyst_enabled_count"] == 0
    assert payload["analyst_resolved_count"] == 0

    assert (
        payload["analyst_average_confidence"]
        is None
    )
    assert (
        payload["analyst_coverage_percentage"]
        == 0.0
    )

    assert (
        payload["analyst_coverage_state"]
        == "UNAVAILABLE"
    )
    assert (
        payload["analyst_coverage_message"]
        == "No analyst domains are available."
    )
    assert (
        payload["analyst_operational_status"]
        == "UNAVAILABLE"
    )
    assert (
        payload["analyst_operational_message"]
        == "No analyst domains are available."
    )
    assert (
        payload["analyst_operational_percentage"]
        == 0.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 0
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 0
    )
    assert (
        payload["analyst_enabled_average_confidence"]
        is None
    )
    assert payload["analyst_domain_count"] == 0
    assert payload["analyst_enabled_count"] == 0
    assert payload["analyst_resolved_count"] == 0
    assert payload["analyst_confidence_count"] == 0
    assert (
        payload["analyst_enabled_confidence_count"]
        == 0
    )
    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 0.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 0.0
    )


def test_result_update_is_combined_with_health(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish(
        make_health(
            cycle_count=1
        )
    )

    publisher.publish(
        make_result()
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["latest_cycle_status"]
        == "SKIPPED_NO_NEW_BAR"
    )

    assert (
        payload["latest_cycle_message"]
        == "No new completed bar."
    )

    assert payload["has_cycle"] is True
    assert payload["cycle_failed"] is False


def test_result_before_health_is_retained(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish(
        make_result()
    )

    assert output_path.exists() is False

    publisher.publish(
        make_health(
            cycle_count=1
        )
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["latest_cycle_status"]
        == "SKIPPED_NO_NEW_BAR"
    )


def test_market_session_can_be_updated(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish(
        make_health()
    )

    publisher.update_market_session(
        "REGULAR"
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
    payload["market_session"]
    == "REGULAR"
    )


def test_latest_decision_can_be_updated(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish(
        make_health()
    )

    publisher.update_latest_decision(
        "WAIT"
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["latest_decision"]
        == "WAIT"
    )


def test_publish_rejects_unknown_type(
    tmp_path: Path,
) -> None:
    publisher = DashboardStatusFilePublisher(
        path=(
            tmp_path
            / "dashboard.json"
        ),
        symbol="NVDA",
        timeframe="2m",
    )

    with pytest.raises(
        TypeError,
        match="RuntimeHealthSummary",
    ):
        publisher.publish(
            object(),  # type: ignore[arg-type]
        )


def test_publish_result_populates_market_session(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        make_completed_result()
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["market_session"]
        == DEFAULT_SESSION_STATE.value
    )

def test_publish_result_populates_latest_decision(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        make_completed_result()
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["latest_decision"]
        == DirectorDecision.PREPARE.value
    )

def test_skipped_cycle_retains_latest_decision(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
    make_health()
    )

    publisher.publish_result(
        make_completed_result()
    )

    publisher.publish_result(
        AnalysisCycleResult(
            status=(
                AnalysisCycleStatus
                .SKIPPED_NO_NEW_BAR
            ),
            symbol="NVDA",
            timeframe="2m",
            started_at=(
                NOW
                + timedelta(
                    seconds=5
                )
            ),
            completed_at=(
                NOW
                + timedelta(
                    seconds=5
                )
            ),
            message="No new completed bar.",
        )
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["latest_cycle_status"]
        == "SKIPPED_NO_NEW_BAR"
    )

    assert (
        payload["latest_decision"]
        == DirectorDecision.PREPARE.value
    )

def test_session_skipped_result_populates_market_session(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    market_session = make_market_session(
        MarketSessionState.CLOSED
    )

    session_policy = SessionPolicyResult(
        action=SessionPolicyAction.SKIP,
        session=market_session,
        reason=(
            "Runtime analysis is disabled during "
            "the CLOSED session."
        ),
    )

    result = AnalysisCycleResult(
        status=(
            AnalysisCycleStatus
            .SKIPPED_SESSION
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=NOW,
        message=session_policy.reason,
        market_session=market_session,
        session_policy=session_policy,
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["market_session"]
        == MarketSessionState.CLOSED.value
    )

    assert (
        payload["latest_decision"]
        is None
    )

def test_publish_result_populates_trade_plan_details(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        make_completed_result_with_trade_plan()
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["trade_plan_valid"] is True
    assert payload["trade_direction"] == "long"
    assert payload["trade_entry"] == 500.0
    assert payload["trade_stop"] == 499.0
    assert payload["trade_target1"] == 501.0
    assert payload["trade_target2"] == 502.0
    assert payload["trade_rr1"] == 1.0
    assert payload["trade_rr2"] == 2.0
    assert payload["trade_quality"] == 90
    assert (
        payload["trade_narrative"]
        == "The proposed TradePlan is valid."
    )

    assert payload["trade_reasons"] == [
        "Risk validation passed.",
    ]

    assert payload["trade_warnings"] == []

    assert payload["institutional_bias"] == "BULLISH"

    assert (
        payload["institutional_bias_confidence"]
        == 88.0
    )

    assert (
        payload["institutional_bias_strength"]
        == 80.0
    )

    assert (
        payload["institutional_bias_bullish_score"]
        == 90.0
    )

    assert (
        payload["institutional_bias_bearish_score"]
        == 10.0
    )

    assert (
        payload["institutional_bias_agreement_count"]
        == 3
    )

    assert (
        payload["institutional_bias_conflict_count"]
        == 1
    )

    assert (
        payload["institutional_bias_supporting_domains"]
        == [
            "STRUCTURE",
            "LIQUIDITY",
            "TREND",
        ]
    )

    assert (
        payload["institutional_bias_opposing_domains"]
        == [
            "VALUE",
        ]
    )

    assert payload["market_phase"] == "MARKUP"

    assert (
        payload["market_phase_confidence"]
        == 84.0
    )

    assert (
        payload["confluence_direction"]
        == "BULLISH"
    )

    assert payload["confluence_score"] == 100.0

    assert (
        payload["confluence_agreement_count"]
        == 3
    )

    assert (
        payload["confluence_conflict_count"]
        == 0
    )

    assert (
        payload["market_phase_strength"]
        == 80.0
    )

    assert (
        payload["market_phase_agreement_count"]
        == 5
    )

    assert (
        payload["market_phase_conflict_count"]
        == 1
    )

    assert (
        payload["market_phase_supporting_domains"]
        == [
            "STRUCTURE",
            "AUCTION",
            "TREND",
        ]
    )

    assert (
        payload["market_phase_opposing_domains"]
        == [
            "VALUE",
        ]
    )
    assert payload["setup_lifecycle_state"] == "READY"

    assert (
        payload["setup_lifecycle_direction"]
        == "long"
    )

    assert (
        payload["setup_lifecycle_confidence"]
        == 90.0
    )

    assert (
        payload["setup_lifecycle_atr_distance"]
        == 0.10
    )

    assert (
        payload["setup_lifecycle_action"]
        == "EVALUATE_ENTRY"
    )

    assert (
        payload["setup_lifecycle_reason"]
        == "Setup lifecycle is ready."
    )

    assert payload["acceptance_confirmed"] is True
    assert payload["acceptance_direction"] == "long"
    assert payload["acceptance_level"] == "STRONG"
    assert payload["acceptance_score"] == 90
    assert payload["acceptance_confidence"] == 90.0
    assert payload["acceptance_trigger_price"] == 500.0
    assert payload["acceptance_previous_level"] == 499.75
    assert payload["acceptance_pullback_low"] == 499.0
    assert payload["acceptance_pullback_high"] == 500.0
    assert (
        payload["acceptance_reason"]
        == "Acceptance confirmed."
    )
    assert payload["acceptance_evidence"] == [
        "Completed-candle acceptance confirmed.",
    ]
    assert payload["acceptance_warnings"] == []

    assert (
        payload["confluence_confidence_adjustment"]
        == 8.0
    )

    assert (
        payload["confluence_structure_support"]
        is True
    )

    assert (
        payload["confluence_liquidity_support"]
        is True
    )

    assert (
        payload["confluence_order_block_support"]
        is True
    )

    assert (
        payload["confluence_auction_support"]
        is False
    )

    assert (
        payload["confluence_pressure_support"]
        is False
    )

    assert (
        payload["confluence_participation_support"]
        is False
    )

    assert (
        payload["confluence_value_support"]
        is False
    )

    assert payload["confluence_bullish_count"] == 3
    assert payload["confluence_bearish_count"] == 0
    assert payload["confluence_neutral_count"] == 0
    assert payload["confluence_unknown_count"] == 0
    assert payload["confluence_domain_count"] == 3

    assert payload["acceptance_confirmed"] is True
    assert payload["acceptance_direction"] == "long"
    assert payload["acceptance_level"] == "STRONG"
    assert payload["acceptance_score"] == 90
    assert payload["acceptance_confidence"] == 90.0
    assert payload["acceptance_trigger_price"] == 500.0
    assert payload["acceptance_previous_level"] == 499.75
    assert payload["acceptance_pullback_low"] == 499.0
    assert payload["acceptance_pullback_high"] == 500.0

    assert (
        payload["acceptance_reason"]
        == "Acceptance confirmed."
    )

    assert payload["acceptance_evidence"] == [
        "Completed-candle acceptance confirmed.",
    ]

    assert payload["acceptance_warnings"] == []

    assert payload["trend_analyst"] == "TrendAnalyst"
    assert payload["trend_opinion"] == "BULLISH"
    assert payload["trend_confidence"] == 90.0
    assert payload["trend_enabled"] is True

    assert payload["trend_evidence"] == [
        "Price is above EMA9 and VWAP.",
    ]

    assert payload["trend_warnings"] == []
    assert payload["structure_analyst"] == "STRUCTURE"

    assert payload["structure_opinion"] == (
        "Bullish structure continuation is confirmed."
    )

    assert payload["structure_confidence"] == 84.0
    assert payload["structure_enabled"] is True

    assert payload["liquidity_analyst"] == "LIQUIDITY"

    assert payload["liquidity_opinion"] == (
        "Sell-side liquidity remains active."
    )

    assert payload["liquidity_confidence"] == 78.0
    assert payload["liquidity_enabled"] is True

    assert payload["order_block_analyst"] == "ORDER_BLOCK"

    assert payload["order_block_opinion"] == (
        "Bullish order block remains valid."
    )

    assert payload["order_block_confidence"] == 81.0
    assert payload["order_block_enabled"] is True

    assert payload["order_block_analyst"] == "ORDER_BLOCK"

    assert payload["order_block_opinion"] == (
        "Bullish order block remains valid."
    )

    assert payload["order_block_confidence"] == 81.0
    assert payload["order_block_enabled"] is True

    assert payload["auction_analyst"] == "AUCTION"

    assert payload["auction_opinion"] == (
        "Buyers maintain auction control."
    )

    assert payload["auction_confidence"] == 79.0
    assert payload["auction_enabled"] is True

    assert payload["pressure_analyst"] == "PRESSURE"

    assert payload["pressure_opinion"] == (
        "Buying pressure remains dominant."
    )

    assert payload["pressure_confidence"] == 77.0
    assert payload["pressure_enabled"] is True

    assert (
        payload["participation_analyst"]
        == "PARTICIPATION"
    )

    assert payload["participation_opinion"] == (
        "Institutional participation is expanding."
    )

    assert payload["participation_confidence"] == 76.0
    assert payload["participation_enabled"] is True

    assert payload["value_analyst"] == "VALUE"

    assert payload["value_opinion"] == (
        "Price remains within fair value."
    )

    assert payload["value_confidence"] == 74.0
    assert payload["value_enabled"] is True

    assert payload["analyst_domain_count"] == 8
    assert payload["analyst_enabled_count"] == 8
    assert payload["analyst_resolved_count"] == 8

    assert (
        payload["analyst_average_confidence"]
        == pytest.approx(
            78.875
        )
    )
    assert (
        payload["analyst_coverage_percentage"]
        == 100.0
    )

    assert (
        payload["analyst_coverage_state"]
        == "COMPLETE"
    )
    assert (
        payload["analyst_coverage_message"]
        == (
            "All 8 analyst domains have produced "
            "an opinion."
        )
    )
    assert (
        payload["analyst_operational_status"]
        == "OPERATIONAL"
    )
    assert (
        payload["analyst_operational_message"]
        == (
            "All 8 enabled analyst domains "
            "have produced an opinion."
        )
    )
    assert (
        payload["analyst_operational_percentage"]
        == 100.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 8
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 0
    )


def test_publish_result_uses_empty_institutional_fields_when_context_is_missing(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        make_completed_result()
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["institutional_bias"] is None

    assert (
        payload["institutional_bias_confidence"]
        is None
    )

    assert payload["market_phase"] is None

    assert (
        payload["market_phase_confidence"]
        is None
    )

    assert payload["confluence_direction"] is None
    assert payload["confluence_score"] is None

    assert (
        payload["confluence_agreement_count"]
        is None
    )

    assert (
        payload["confluence_conflict_count"]
        is None
    )

    assert payload["market_phase_strength"] is None

    assert (
        payload["market_phase_agreement_count"]
        is None
    )

    assert (
        payload["market_phase_conflict_count"]
        is None
    )

    assert (
        payload["market_phase_supporting_domains"]
        == []
    )

    assert (
        payload["market_phase_opposing_domains"]
        == []
    )

    assert (
        payload["institutional_bias_strength"]
        is None
    )

    assert (
        payload["institutional_bias_bullish_score"]
        is None
    )

    assert (
        payload["institutional_bias_bearish_score"]
        is None
    )

    assert (
        payload["institutional_bias_agreement_count"]
        is None
    )

    assert (
        payload["institutional_bias_conflict_count"]
        is None
    )

    assert (
        payload["institutional_bias_supporting_domains"]
        == []
    )

    assert (
        payload["institutional_bias_opposing_domains"]
        == []
    )
    assert (
        payload["confluence_confidence_adjustment"]
        is None
    )

    assert (
        payload["confluence_structure_support"]
        is None
    )

    assert (
        payload["confluence_liquidity_support"]
        is None
    )

    assert (
        payload["confluence_order_block_support"]
        is None
    )

    assert (
        payload["confluence_auction_support"]
        is None
    )

    assert (
        payload["confluence_pressure_support"]
        is None
    )

    assert (
        payload["confluence_participation_support"]
        is None
    )

    assert (
        payload["confluence_value_support"]
        is None
    )

    assert payload["confluence_bullish_count"] is None
    assert payload["confluence_bearish_count"] is None
    assert payload["confluence_neutral_count"] is None
    assert payload["confluence_unknown_count"] is None
    assert payload["confluence_domain_count"] is None

    assert payload["setup_lifecycle_state"] is None

    assert (
        payload["setup_lifecycle_direction"]
        is None
    )

    assert (
        payload["setup_lifecycle_confidence"]
        is None
    )

    assert (
        payload["setup_lifecycle_atr_distance"]
        is None
    )

    assert (
        payload["setup_lifecycle_action"]
        is None
    )

    assert (
        payload["setup_lifecycle_reason"]
        is None
    )
    assert payload["acceptance_confirmed"] is None
    assert payload["acceptance_direction"] is None
    assert payload["acceptance_level"] is None
    assert payload["acceptance_score"] is None
    assert payload["acceptance_confidence"] is None
    assert payload["acceptance_trigger_price"] is None
    assert payload["acceptance_previous_level"] is None
    assert payload["acceptance_pullback_low"] is None
    assert payload["acceptance_pullback_high"] is None
    assert payload["acceptance_reason"] is None
    assert payload["acceptance_evidence"] == []
    assert payload["acceptance_warnings"] == []
    assert payload["acceptance_confirmed"] is None
    assert payload["acceptance_direction"] is None
    assert payload["acceptance_level"] is None
    assert payload["acceptance_score"] is None
    assert payload["acceptance_confidence"] is None
    assert payload["acceptance_trigger_price"] is None
    assert payload["acceptance_previous_level"] is None
    assert payload["acceptance_pullback_low"] is None
    assert payload["acceptance_pullback_high"] is None
    assert payload["acceptance_reason"] is None
    assert payload["acceptance_evidence"] == []
    assert payload["acceptance_warnings"] == []

    assert payload["trend_analyst"] is None
    assert payload["trend_opinion"] is None
    assert payload["trend_confidence"] is None
    assert payload["trend_enabled"] is None
    assert payload["trend_evidence"] == []
    assert payload["trend_warnings"] == []


def test_publish_result_calculates_partial_analyst_coverage(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    decision = make_decision()

    decision = DecisionResult(
        decision=decision.decision,
        actionable=decision.actionable,
        confidence=decision.confidence,
        recommendation=decision.recommendation,
        reasons=decision.reasons,
        warnings=decision.warnings,
        analyst_summary={
            "TREND": {
                "opinion": "Bullish.",
                "confidence": 80.0,
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "",
                "confidence": 60.0,
                "enabled": False,
            },
        },
        trade_plan=decision.trade_plan,
        institutional_context=(
            decision.institutional_context
        ),
    )

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=(
            NOW
            + timedelta(
                seconds=2
            )
        ),
        message="Analysis cycle completed.",
        market_session=make_market_session(),
        decision=decision,
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["analyst_domain_count"] == 2
    assert payload["analyst_enabled_count"] == 1
    assert payload["analyst_resolved_count"] == 1

    assert (
        payload["analyst_average_confidence"]
        == 70.0
    )

    assert (
        payload["analyst_enabled_average_confidence"]
        == 80.0
    )
    assert (
        payload["analyst_coverage_percentage"]
        == 50.0
    )

    assert (
        payload["analyst_coverage_state"]
        == "PARTIAL"
    )

    assert (
        payload["analyst_coverage_message"]
        == (
            "1 of 2 analyst domains have produced "
            "an opinion."
        )
    )

    assert (
        payload["analyst_operational_status"]
        == "OPERATIONAL"
    )
    assert (
        payload["analyst_operational_message"]
        == (
            "All 1 enabled analyst domains "
            "have produced an opinion."
        )
    )
    assert (
        payload["analyst_operational_percentage"]
        == 100.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 1
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 0
    )
    assert payload["analyst_confidence_count"] == 2
    assert (
        payload["analyst_enabled_confidence_count"]
        == 1
    )
    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 100.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 100.0
    )


def test_publish_result_marks_unresolved_analyst_coverage(
        tmp_path: Path,
    ) -> None:
        path = (
            tmp_path
            / "dashboard.json"
        )

        publisher = DashboardStatusFilePublisher(
            path=path,
            symbol="NVDA",
            timeframe="2m",
        )

        decision = make_decision()

        decision = DecisionResult(
            decision=decision.decision,
            actionable=decision.actionable,
            confidence=decision.confidence,
            recommendation=decision.recommendation,
            reasons=decision.reasons,
            warnings=decision.warnings,
            analyst_summary={
                "TREND": {
                    "opinion": "",
                    "confidence": 80.0,
                    "enabled": True,
                },
                "LIQUIDITY": {
                    "opinion": "   ",
                    "confidence": 60.0,
                    "enabled": True,
                },
            },
            trade_plan=decision.trade_plan,
            institutional_context=(
                decision.institutional_context
            ),
        )

        result = AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=NOW,
            completed_at=(
                NOW
                + timedelta(
                    seconds=2
                )
            ),
            message="Analysis cycle completed.",
            market_session=make_market_session(),
            decision=decision,
        )

        publisher.publish_health(
            make_health()
        )

        publisher.publish_result(
            result
        )

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        assert payload["analyst_domain_count"] == 2
        assert payload["analyst_resolved_count"] == 0

        assert (
            payload["analyst_coverage_percentage"]
            == 0.0
        )

        assert (
            payload["analyst_coverage_state"]
            == "UNRESOLVED"
        )

        assert (
            payload["analyst_coverage_message"]
            == (
                "Analyst domains are available, but none "
                "have produced an opinion."
            )
        )
        assert (
            payload["analyst_operational_status"]
            == "UNRESOLVED"
        )
        assert (
            payload["analyst_operational_message"]
            == (
                "Enabled analyst domains have not "
                "produced an opinion."
            )
        )
        assert (
            payload["analyst_operational_percentage"]
            == 0.0
        )
        assert (
            payload["analyst_enabled_resolved_count"]
            == 0
        )
        assert (
            payload["analyst_enabled_unresolved_count"]
            == 2
        )

def test_publish_result_marks_disabled_analyst_operation(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "",
                "confidence": 0.0,
                "enabled": False,
            },
            "LIQUIDITY": {
                "opinion": "",
                "confidence": 0.0,
                "enabled": False,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_operational_status"]
        == "DISABLED"
    )
    assert (
        payload["analyst_operational_message"]
        == "All analyst domains are disabled."
    )
    assert (
        payload["analyst_operational_percentage"]
        == 0.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 0
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 0
    )

def test_publish_result_marks_degraded_analyst_operation(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": (
                    "Directional trend is bullish."
                ),
                "confidence": 82.0,
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "",
                "confidence": 0.0,
                "enabled": True,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_operational_status"]
        == "DEGRADED"
    )
    assert (
        payload["analyst_operational_message"]
        == (
            "1 of 2 enabled analyst domains "
            "have produced an opinion."
        )
    )
    assert (
        payload["analyst_operational_percentage"]
        == 50.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 1
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 1
    )


def test_disabled_unresolved_analyst_does_not_degrade_operation(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "dashboard.json"
    )

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": (
                    "Directional trend is bullish."
                ),
                "confidence": 82.0,
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "",
                "confidence": 0.0,
                "enabled": False,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )

    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_operational_status"]
        == "OPERATIONAL"
    )
    assert (
        payload["analyst_operational_message"]
        == (
            "All 1 enabled analyst domains "
            "have produced an opinion."
        )
    )
    assert (
        payload["analyst_operational_percentage"]
        == 100.0
    )
    assert (
        payload["analyst_enabled_resolved_count"]
        == 1
    )
    assert (
        payload["analyst_enabled_unresolved_count"]
        == 0
    )

def test_publish_result_calculates_enabled_average_confidence(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    decision = make_decision()

    decision = DecisionResult(
        decision=decision.decision,
        actionable=decision.actionable,
        confidence=decision.confidence,
        recommendation=decision.recommendation,
        reasons=decision.reasons,
        warnings=decision.warnings,
        analyst_summary={
            "TREND": {
                "opinion": "Bullish.",
                "confidence": 80.0,
                "enabled": True,
            },
            "STRUCTURE": {
                "opinion": "Bullish continuation.",
                "confidence": 60.0,
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "Balanced.",
                "confidence": 20.0,
                "enabled": False,
            },
        },
        trade_plan=decision.trade_plan,
        institutional_context=(
            decision.institutional_context
        ),
    )

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=NOW,
        completed_at=NOW + timedelta(seconds=2),
        message="Analysis cycle completed.",
        market_session=make_market_session(),
        decision=decision,
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_average_confidence"]
        == pytest.approx(160.0 / 3.0)
    )

    assert (
        payload["analyst_enabled_average_confidence"]
        == 70.0
    )
    assert payload["analyst_confidence_count"] == 3
    assert (
        payload["analyst_enabled_confidence_count"]
        == 2
    )
    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 100.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 100.0
    )

def test_publish_result_calculates_partial_confidence_coverage(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "Bullish.",
                "confidence": 80.0,
                "enabled": True,
            },
            "STRUCTURE": {
                "opinion": "Bullish continuation.",
                "enabled": True,
            },
            "LIQUIDITY": {
                "opinion": "Balanced.",
                "confidence": 60.0,
                "enabled": False,
            },
            "VALUE": {
                "opinion": "Neutral.",
                "enabled": False,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["analyst_domain_count"] == 4
    assert payload["analyst_confidence_count"] == 2

    assert payload["analyst_enabled_count"] == 2
    assert (
        payload["analyst_enabled_confidence_count"]
        == 1
    )

    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 50.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 50.0
    )
    assert (
        payload["analyst_confidence_coverage_state"]
        == "PARTIAL"
    )
    assert (
        payload["analyst_confidence_coverage_message"]
        == "Confidence is available for 2 of 4 analyst domains."
    )

    assert (
        payload[
            "analyst_enabled_confidence_coverage_state"
        ]
        == "PARTIAL"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == (
            "Confidence is available for 1 of 2 "
            "enabled analyst domains."
        )
    )
    assert (
        payload["analyst_missing_confidence_count"]
        == 2
    )
    assert (
        payload[
            "analyst_enabled_missing_confidence_count"
        ]
        == 1
    )

def test_zero_confidence_counts_as_available(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "No directional confidence.",
                "confidence": 0.0,
                "enabled": True,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["analyst_confidence_count"] == 1
    assert (
        payload["analyst_enabled_confidence_count"]
        == 1
    )
    assert (
        payload["analyst_confidence_coverage_percentage"]
        == 100.0
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_percentage"
        ]
        == 100.0
    )
    assert (
        payload["analyst_confidence_coverage_state"]
        == "COMPLETE"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_state"
        ]
        == "COMPLETE"
    )
    assert (
        payload["analyst_confidence_coverage_message"]
        == "Confidence is available for all 1 analyst domain."
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == (
            "Confidence is available for all "
            "1 enabled analyst domain."
        )
    )
    assert (
        payload["analyst_missing_confidence_count"]
        == 0
    )
    assert (
        payload[
            "analyst_enabled_missing_confidence_count"
        ]
        == 0
    )

def test_publish_result_reports_missing_confidence_coverage(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "Trend is unresolved.",
                "enabled": True,
            },
            "STRUCTURE": {
                "opinion": "Structure is unresolved.",
                "enabled": True,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_confidence_coverage_state"]
        == "MISSING"
    )
    assert (
        payload["analyst_confidence_coverage_message"]
        == (
            "Confidence is unavailable for all "
            "2 analyst domains."
        )
    )

    assert (
        payload[
            "analyst_enabled_confidence_coverage_state"
        ]
        == "MISSING"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == (
            "Confidence is unavailable for all "
            "2 enabled analyst domains."
        )
    )
    assert (
        payload["analyst_missing_confidence_count"]
        == 2
    )
    assert (
        payload[
            "analyst_enabled_missing_confidence_count"
        ]
        == 2
    )

def test_publish_result_reports_disabled_enabled_confidence_coverage(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "Trend is disabled.",
                "confidence": 70.0,
                "enabled": False,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_confidence_coverage_state"]
        == "COMPLETE"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_state"
        ]
        == "DISABLED"
    )
    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == "No analyst domains are enabled."
    )

def test_publish_result_uses_singular_missing_confidence_message(
    tmp_path: Path,
) -> None:
    path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=path,
        symbol="NVDA",
        timeframe="2m",
    )

    result = make_completed_result_with_analyst_summary(
        {
            "TREND": {
                "opinion": "Trend is unresolved.",
                "enabled": True,
            },
        }
    )

    publisher.publish_health(
        make_health()
    )
    publisher.publish_result(
        result
    )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["analyst_confidence_coverage_message"]
        == (
            "Confidence is unavailable for all "
            "1 analyst domain."
        )
    )

    assert (
        payload[
            "analyst_enabled_confidence_coverage_message"
        ]
        == (
            "Confidence is unavailable for all "
            "1 enabled analyst domain."
        )
    )

@pytest.mark.parametrize(
    "indent",
    (
        None,
        0,
        2,
        4,
    ),
)
def test_written_file_matches_dashboard_status_json(
    tmp_path: Path,
    indent: int | None,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=indent,
    )

    health = make_health()
    publisher.publish_health(
        health
    )

    expected = (
        publisher
        .build_status()
        .to_json(
            indent=indent,
        )
        + "\n"
    )

    assert output_path.read_text(
        encoding="utf-8",
    ) == expected

def test_compact_publisher_output_uses_canonical_format(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=None,
    )

    publisher.publish_health(
        make_health()
    )

    serialized = output_path.read_text(
        encoding="utf-8",
    )

    assert serialized.endswith(
        "\n"
    )
    assert serialized.count(
        "\n"
    ) == 1
    assert ": " not in serialized
    assert ", " not in serialized

    assert json.loads(
        serialized
    ) == (
        publisher
        .build_status()
        .to_dict()
    )

@pytest.mark.parametrize(
    "indent",
    (
        0,
        2,
        4,
    ),
)
def test_indented_publisher_output_is_multiline(
    tmp_path: Path,
    indent: int,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=indent,
    )

    publisher.publish_health(
        make_health()
    )

    serialized = output_path.read_text(
        encoding="utf-8",
    )

    assert serialized.endswith(
        "\n"
    )
    assert serialized.count(
        "\n"
    ) > 1

    assert json.loads(
        serialized
    ) == (
        publisher
        .build_status()
        .to_dict()
    )

def test_subsequent_publication_overwrites_previous_json(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    first_serialized = output_path.read_text(
        encoding="utf-8",
    )

    publisher.publish_health(
        make_health(
            cycle_count=7,
        )
    )

    second_serialized = output_path.read_text(
        encoding="utf-8",
    )
    second_payload = json.loads(
        second_serialized
    )

    assert second_serialized != first_serialized
    assert second_payload[
        "completed_cycle_count"
    ] == 7

    assert second_serialized == (
        publisher
        .build_status()
        .to_json(
            indent=2,
        )
        + "\n"
    )

def test_successful_publication_removes_temporary_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    assert output_path.exists()
    assert temporary_path.exists() is False

@pytest.mark.parametrize(
    "indent",
    (
        None,
        0,
        2,
        4,
    ),
)
@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_non_finite_payload_preserves_existing_dashboard_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    indent: int | None,
    non_finite_value: float,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=indent,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    original_content = output_path.read_text(
        encoding="utf-8",
    )

    invalid_status = publisher.build_status()

    object.__setattr__(
        invalid_status,
        "trend_confidence",
        non_finite_value,
    )

    monkeypatch.setattr(
        publisher,
        "build_status",
        lambda: invalid_status,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == original_content

@pytest.mark.parametrize(
    "non_finite_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_non_finite_payload_leaves_no_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    non_finite_value: float,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    invalid_status = publisher.build_status()

    object.__setattr__(
        invalid_status,
        "analyst_operational_percentage",
        non_finite_value,
    )

    monkeypatch.setattr(
        publisher,
        "build_status",
        lambda: invalid_status,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        publisher.update_latest_decision(
            "WAIT"
        )

    assert temporary_path.exists() is False
    assert output_path.exists()

@pytest.mark.parametrize(
    "indent",
    (
        None,
        0,
        2,
        4,
    ),
)
def test_failed_first_serialization_creates_no_dashboard_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    indent: int | None,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=indent,
    )

    publisher._health = make_health()

    invalid_status = publisher.build_status()

    object.__setattr__(
        invalid_status,
        "trend_confidence",
        float("nan"),
    )

    monkeypatch.setattr(
        publisher,
        "build_status",
        lambda: invalid_status,
    )

    with pytest.raises(
        ValueError,
        match="JSON compliant",
    ):
        publisher.update_market_session(
            "REGULAR"
        )

    assert output_path.exists() is False
    assert temporary_path.exists() is False

def test_temporary_write_failure_preserves_existing_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    original_content = output_path.read_text(
        encoding="utf-8",
    )
    original_write_text = Path.write_text

    def failing_write_text(
        path: Path,
        data: str,
        *,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        if path == temporary_path:
            raise OSError(
                "Temporary dashboard write failed."
            )

        return original_write_text(
            path,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "write_text",
        failing_write_text,
    )

    with pytest.raises(
        OSError,
        match="Temporary dashboard write failed",
    ):
        publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == original_content
    assert temporary_path.exists() is False

def test_first_temporary_write_failure_creates_no_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    original_write_text = Path.write_text

    def failing_write_text(
        path: Path,
        data: str,
        *,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        if path == temporary_path:
            raise PermissionError(
                "Dashboard directory is read-only."
            )

        return original_write_text(
            path,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "write_text",
        failing_write_text,
    )

    with pytest.raises(
        PermissionError,
        match="read-only",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.exists() is False
    assert temporary_path.exists() is False

def test_atomic_replace_failure_preserves_existing_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    original_content = output_path.read_text(
        encoding="utf-8",
    )

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        raise OSError(
            "Atomic dashboard replacement failed."
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )

    with pytest.raises(
        OSError,
        match="Atomic dashboard replacement failed",
    ):
        publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == original_content
    assert temporary_path.exists() is False

def test_first_atomic_replace_failure_leaves_no_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        raise PermissionError(
            "Dashboard replacement is not permitted."
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )

    with pytest.raises(
        PermissionError,
        match="not permitted",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.exists() is False
    assert temporary_path.exists() is False

def test_atomic_replace_uses_expected_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_calls: list[
        tuple[Path, Path]
    ] = []
    original_replace = os.replace

    def recording_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        replace_calls.append(
            (
                Path(source),
                Path(destination),
            )
        )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        recording_replace,
    )

    publisher.publish_health(
        make_health()
    )

    assert replace_calls == [
        (
            temporary_path,
            output_path,
        )
    ]
    assert output_path.exists()
    assert temporary_path.exists() is False

def test_concurrent_health_updates_leave_valid_dashboard_json(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    cycle_counts = tuple(
        range(
            1,
            21,
        )
    )

    with ThreadPoolExecutor(
        max_workers=8,
    ) as executor:
        futures = tuple(
            executor.submit(
                publisher.publish_health,
                make_health(
                    cycle_count=cycle_count,
                ),
            )
            for cycle_count in cycle_counts
        )

        for future in futures:
            future.result()

    serialized = output_path.read_text(
        encoding="utf-8",
    )
    payload = json.loads(
        serialized
    )

    assert payload[
        "completed_cycle_count"
    ] in cycle_counts

    assert payload["state"] == "RUNNING"
    assert payload["symbol"] == "NVDA"
    assert payload["timeframe"] == "2m"

    assert serialized == (
        publisher
        .build_status()
        .to_json(
            indent=2,
        )
        + "\n"
    )

def test_concurrent_decision_updates_leave_complete_json(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=None,
    )

    publisher.publish_health(
        make_health()
    )

    decisions = (
        "WAIT",
        "PASS",
        "READY",
        "PREPARE",
        "ENTER",
        "HOLD",
        "EXIT",
    )

    with ThreadPoolExecutor(
        max_workers=7,
    ) as executor:
        futures = tuple(
            executor.submit(
                publisher.update_latest_decision,
                decision,
            )
            for decision in decisions
        )

        for future in futures:
            future.result()

    serialized = output_path.read_text(
        encoding="utf-8",
    )
    payload = json.loads(
        serialized
    )

    assert payload[
        "latest_decision"
    ] in decisions

    assert serialized.endswith(
        "\n"
    )
    assert serialized.count(
        "\n"
    ) == 1

    assert serialized == (
        publisher
        .build_status()
        .to_json(
            indent=None,
        )
        + "\n"
    )

def test_concurrent_publications_serialize_temporary_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    original_write_text = Path.write_text
    counter_lock = Lock()
    active_temporary_writes = 0
    maximum_active_temporary_writes = 0

    def recording_write_text(
        path: Path,
        data: str,
        *,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        nonlocal active_temporary_writes
        nonlocal maximum_active_temporary_writes

        if path == temporary_path:
            with counter_lock:
                active_temporary_writes += 1
                maximum_active_temporary_writes = max(
                    maximum_active_temporary_writes,
                    active_temporary_writes,
                )

            try:
                sleep(
                    0.01
                )

                return original_write_text(
                    path,
                    data,
                    encoding=encoding,
                    errors=errors,
                    newline=newline,
                )
            finally:
                with counter_lock:
                    active_temporary_writes -= 1

        return original_write_text(
            path,
            data,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "write_text",
        recording_write_text,
    )

    with ThreadPoolExecutor(
        max_workers=8,
    ) as executor:
        futures = tuple(
            executor.submit(
                publisher.publish_health,
                make_health(
                    cycle_count=cycle_count,
                ),
            )
            for cycle_count in range(
                1,
                17,
            )
        )

        for future in futures:
            future.result()

    assert maximum_active_temporary_writes == 1
    assert active_temporary_writes == 0
    assert temporary_path.exists() is False

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload[
        "completed_cycle_count"
    ] in range(
        1,
        17,
    )

def test_concurrent_mixed_updates_leave_coherent_snapshot(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    operations = (
        lambda: publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        ),
        lambda: publisher.publish_health(
            make_health(
                cycle_count=3,
            )
        ),
        lambda: publisher.update_market_session(
            "PREMARKET"
        ),
        lambda: publisher.update_market_session(
            "REGULAR"
        ),
        lambda: publisher.update_latest_decision(
            "WAIT"
        ),
        lambda: publisher.update_latest_decision(
            "READY"
        ),
    )

    with ThreadPoolExecutor(
        max_workers=len(
            operations
        ),
    ) as executor:
        futures = tuple(
            executor.submit(
                operation
            )
            for operation in operations
        )

        for future in futures:
            future.result()

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )
    current_status = publisher.build_status()

    assert payload == current_status.to_dict()

    assert payload[
        "completed_cycle_count"
    ] in {
        2,
        3,
    }
    assert payload[
        "market_session"
    ] in {
        "PREMARKET",
        "REGULAR",
    }
    assert payload[
        "latest_decision"
    ] in {
        "WAIT",
        "READY",
    }

def test_concurrent_readers_only_observe_complete_destination_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=0,
        )
    )

    original_replace = os.replace
    replace_started = Event()
    allow_replace = Event()

    def delayed_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        replace_started.set()

        assert allow_replace.wait(
            timeout=5,
        )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        delayed_replace,
    )

    with ThreadPoolExecutor(
        max_workers=2,
    ) as executor:
        write_future = executor.submit(
            publisher.publish_health,
            make_health(
                cycle_count=1,
            ),
        )

        assert replace_started.wait(
            timeout=5,
        )

        destination_payload = json.loads(
            output_path.read_text(
                encoding="utf-8",
            )
        )
        temporary_payload = json.loads(
            temporary_path.read_text(
                encoding="utf-8",
            )
        )

        assert destination_payload[
            "completed_cycle_count"
        ] == 0

        assert temporary_payload[
            "completed_cycle_count"
        ] == 1

        allow_replace.set()
        write_future.result()

    final_payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert final_payload[
        "completed_cycle_count"
    ] == 1
    assert temporary_path.exists() is False

def test_atomic_replace_retries_transient_permission_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    sleep_calls: list[float] = []
    original_replace = os.replace

    def flaky_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        if replace_attempts == 1:
            raise make_windows_permission_error(
                winerror=32,
            )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        flaky_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    assert replace_attempts == 2
    assert sleep_calls == [
        publisher._REPLACE_RETRY_DELAY_SECONDS,
    ]

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload[
        "completed_cycle_count"
    ] == 1

def test_atomic_replace_can_succeed_on_final_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    original_replace = os.replace

    def flaky_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        if (
            replace_attempts
            < publisher._REPLACE_MAX_ATTEMPTS
        ):
            raise make_windows_permission_error(
                winerror=32,
            )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        flaky_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        lambda _: None,
    )

    publisher.publish_health(
        make_health()
    )

    assert (
        replace_attempts
        == publisher._REPLACE_MAX_ATTEMPTS
    )
    assert output_path.exists()

def test_atomic_replace_raises_after_retry_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    sleep_calls: list[float] = []

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        raise make_windows_permission_error(
            winerror=32,
            message="Destination remained locked.",
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    with pytest.raises(
        PermissionError,
        match="remained locked",
    ):
        publisher.publish_health(
            make_health()
        )

    assert (
        replace_attempts
        == publisher._REPLACE_MAX_ATTEMPTS
    )
    assert len(
        sleep_calls
    ) == (
        publisher._REPLACE_MAX_ATTEMPTS
        - 1
    )
    assert output_path.exists() is False
    assert temporary_path.exists() is False

def test_atomic_replace_does_not_retry_other_os_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    sleep_calls: list[float] = []

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        raise OSError(
            "Unexpected filesystem failure."
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    with pytest.raises(
        OSError,
        match="Unexpected filesystem failure",
    ):
        publisher.publish_health(
            make_health()
        )

    assert replace_attempts == 1
    assert sleep_calls == []

def test_replace_retry_exhaustion_preserves_existing_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    temporary_path = output_path.with_name(
        f".{output_path.name}.tmp"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    original_content = output_path.read_text(
        encoding="utf-8",
    )
    replace_attempts = 0

    def locked_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        raise make_windows_permission_error(
            winerror=32,
            message="Dashboard destination remained locked.",
        )

    monkeypatch.setattr(
        os,
        "replace",
        locked_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        lambda _: None,
    )

    with pytest.raises(
        PermissionError,
        match="remained locked",
    ):
        publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        )

    assert (
        replace_attempts
        == publisher._REPLACE_MAX_ATTEMPTS
    )
    assert output_path.read_text(
        encoding="utf-8",
    ) == original_content
    assert temporary_path.exists() is False

def test_publisher_recovers_after_replace_retry_exhaustion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
        indent=2,
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    original_replace = os.replace
    replace_attempts = 0

    def temporarily_locked_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        if (
            replace_attempts
            <= publisher._REPLACE_MAX_ATTEMPTS
        ):
            raise make_windows_permission_error(
                winerror=32,
                message="Dashboard destination remained locked.",
            )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        temporarily_locked_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        lambda _: None,
    )

    with pytest.raises(
        PermissionError,
        match="remained locked",
    ):
        publisher.publish_health(
            make_health(
                cycle_count=2,
            )
        )

    publisher.publish_health(
        make_health(
            cycle_count=3,
        )
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload[
        "completed_cycle_count"
    ] == 3
    assert (
        replace_attempts
        == publisher._REPLACE_MAX_ATTEMPTS
        + 1
    )

def test_replace_retry_delay_occurs_only_between_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    sleep_calls: list[float] = []

    def locked_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        raise make_windows_permission_error(
            winerror=32,
        )

    monkeypatch.setattr(
        os,
        "replace",
        locked_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    with pytest.raises(
        PermissionError,
    ):
        publisher.publish_health(
            make_health()
        )

    assert sleep_calls == [
        publisher._REPLACE_RETRY_DELAY_SECONDS
        for _ in range(
            publisher._REPLACE_MAX_ATTEMPTS - 1
        )
    ]

def test_successful_atomic_replace_does_not_sleep(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    sleep_calls: list[float] = []

    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    publisher.publish_health(
        make_health()
    )

    assert sleep_calls == []
    assert output_path.exists()

@pytest.mark.parametrize(
    "winerror",
    [
        5,
        32,
        33,
    ],
)
def test_transient_windows_replace_errors_are_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    winerror: int,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    original_replace = os.replace
    replace_attempts = 0

    def flaky_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        if replace_attempts == 1:
            raise make_windows_permission_error(
                winerror=winerror,
            )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        flaky_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        lambda _: None,
    )

    publisher.publish_health(
        make_health()
    )

    assert replace_attempts == 2
    assert output_path.exists()

@pytest.mark.parametrize(
    "winerror",
    [
        1,
        2,
        3,
        87,
    ],
)
def test_non_transient_windows_permission_errors_are_not_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    winerror: int,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    sleep_calls: list[float] = []

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        raise make_windows_permission_error(
            winerror=winerror,
            message="Permanent permission failure.",
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    with pytest.raises(
        PermissionError,
        match="Permanent permission failure",
    ):
        publisher.publish_health(
            make_health()
        )

    assert replace_attempts == 1
    assert sleep_calls == []

def test_permission_error_without_winerror_is_not_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    replace_attempts = 0
    sleep_calls: list[float] = []

    def failing_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        nonlocal replace_attempts

        replace_attempts += 1

        raise PermissionError(
            "Permission denied."
        )

    monkeypatch.setattr(
        os,
        "replace",
        failing_replace,
    )
    monkeypatch.setattr(
        "imie.runtime.dashboard_status_file_publisher.sleep",
        sleep_calls.append,
    )

    with pytest.raises(
        PermissionError,
        match="Permission denied",
    ):
        publisher.publish_health(
            make_health()
        )

    assert replace_attempts == 1
    assert sleep_calls == []
