import json

import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock, Barrier
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

def dashboard_temporary_files(
    directory: Path,
) -> list[Path]:
    return list(
        directory.glob(
            ".dashboard.json.*.tmp"
        )
    )

def is_dashboard_temporary_path(
    path: Path,
    directory: Path,
) -> bool:
    return (
        path.parent == directory
        and path.name.startswith(
            ".dashboard.json."
        )
        and path.name.endswith(
            ".tmp"
        )
    )

def _raise_directory_sync_error(
) -> None:
    raise PermissionError(
        "Directory sync failed."
    )

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

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    publisher.publish_health(
        make_health()
    )

    assert output_path.exists()
    assert dashboard_temporary_files(
    tmp_path
) == []

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

    assert dashboard_temporary_files(
        tmp_path
    ) == []
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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_temporary_write_failure_preserves_existing_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    original_payload = (
        '{"existing": true}\n'
    )

    output_path.write_text(
        original_payload,
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    original_open = Path.open

    def failing_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        if (
            mode == "x"
            and is_dashboard_temporary_path(
                path,
                tmp_path,
            )
        ):
            raise PermissionError(
                "Temporary dashboard write failed."
            )

        return original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "open",
        failing_open,
    )

    with pytest.raises(
        PermissionError,
        match="Temporary dashboard write failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == original_payload

    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_first_temporary_write_failure_creates_no_dashboard(
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

    original_open = Path.open

    def failing_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        if (
            mode == "x"
            and is_dashboard_temporary_path(
                path,
                tmp_path,
            )
        ):
            raise PermissionError(
                "Temporary dashboard write failed."
            )

        return original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "open",
        failing_open,
    )

    with pytest.raises(
        PermissionError,
        match="Temporary dashboard write failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.exists() is False

    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_atomic_replace_failure_preserves_existing_dashboard(
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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_first_atomic_replace_failure_leaves_no_files(
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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_atomic_replace_uses_expected_paths(
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

    assert len(replace_calls) == 1

    source_path, destination_path = (
        replace_calls[0]
    )

    assert source_path.parent == tmp_path
    assert source_path.name.startswith(
        ".dashboard.json."
    )
    assert source_path.name.endswith(
        ".tmp"
    )
    assert destination_path == output_path

    assert output_path.exists()
    assert source_path.exists() is False
    assert dashboard_temporary_files(
        tmp_path
    ) == []

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

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    original_open = Path.open
    state_lock = Lock()

    active_writes = 0
    maximum_active_writes = 0
    observed_temporary_paths: list[Path] = []

    class DelayedTemporaryFile:
        def __init__(
            self,
            file_object,
            path: Path,
        ) -> None:
            self._file_object = file_object
            self._path = path

        def __enter__(
            self,
        ):
            nonlocal active_writes
            nonlocal maximum_active_writes

            self._file_object.__enter__()

            with state_lock:
                active_writes += 1
                maximum_active_writes = max(
                    maximum_active_writes,
                    active_writes,
                )
                observed_temporary_paths.append(
                    self._path
                )

            return self

        def write(
            self,
            data: str,
        ) -> int:
            sleep(
                0.01
            )

            return self._file_object.write(
                data
            )

        def flush(
            self,
        ) -> None:
            self._file_object.flush()


        def fileno(
            self,
        ) -> int:
            return self._file_object.fileno()

        def __exit__(
            self,
            exception_type,
            exception,
            traceback,
        ):
            nonlocal active_writes

            try:
                return self._file_object.__exit__(
                    exception_type,
                    exception,
                    traceback,
                )

            finally:
                with state_lock:
                    active_writes -= 1

    def delayed_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        file_object = original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

        if (
            mode == "x"
            and is_dashboard_temporary_path(
                path,
                tmp_path,
            )
        ):
            return DelayedTemporaryFile(
                file_object,
                path,
            )

        return file_object

    monkeypatch.setattr(
        Path,
        "open",
        delayed_open,
    )

    publication_count = 16

    with ThreadPoolExecutor(
        max_workers=8,
    ) as executor:
        futures = [
            executor.submit(
                publisher.publish_health,
                make_health(
                    cycle_count=cycle_count,
                ),
            )
            for cycle_count in range(
                1,
                publication_count + 1,
            )
        ]

        for future in futures:
            future.result()

    assert maximum_active_writes == 1

    assert len(
        observed_temporary_paths
    ) == publication_count

    assert len(
        set(
            observed_temporary_paths
        )
    ) == publication_count

    assert dashboard_temporary_files(
        tmp_path
    ) == []

    assert output_path.exists()

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
    temporary_paths: list[Path] = []

    def delayed_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        temporary_paths.append(
            Path(source)
        )

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

        assert len(
            temporary_paths
        ) == 1

        temporary_path = (
            temporary_paths[0]
        )

        assert temporary_path.parent == tmp_path
        assert temporary_path.name.startswith(
            ".dashboard.json."
        )
        assert temporary_path.name.endswith(
            ".tmp"
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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

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
    assert dashboard_temporary_files(
        tmp_path
    ) == []

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

def test_each_publication_uses_unique_temporary_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "dashboard.json"

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    temporary_paths: list[Path] = []
    original_replace = os.replace

    def recording_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        temporary_paths.append(
            Path(source)
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
        make_health(
            cycle_count=1,
        )
    )

    publisher.publish_health(
        make_health(
            cycle_count=2,
        )
    )

    assert len(temporary_paths) == 2
    assert temporary_paths[0] != temporary_paths[1]

    for temporary_path in temporary_paths:
        assert temporary_path.parent == tmp_path
        assert temporary_path.name.startswith(
            ".dashboard.json."
        )
        assert temporary_path.name.endswith(
            ".tmp"
        )
        assert temporary_path.exists() is False

def test_separate_publishers_do_not_share_temporary_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    first_publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )
    second_publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    original_open = Path.open
    recorded_paths: list[Path] = []
    recorded_paths_lock = Lock()
    both_writes_started = Barrier(
        2
    )

    class CoordinatedTemporaryFile:
        def __init__(
            self,
            file_object,
            path: Path,
        ) -> None:
            self._file_object = file_object
            self._path = path

        def __enter__(
            self,
        ):
            entered_file = (
                self._file_object.__enter__()
            )

            with recorded_paths_lock:
                recorded_paths.append(
                    self._path
                )

            both_writes_started.wait(
                timeout=2.0
            )

            return entered_file

        def __exit__(
            self,
            exception_type,
            exception,
            traceback,
        ):
            return self._file_object.__exit__(
                exception_type,
                exception,
                traceback,
            )

    def recording_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        file_object = original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

        if (
            mode == "x"
            and is_dashboard_temporary_path(
                path,
                tmp_path,
            )
        ):
            return CoordinatedTemporaryFile(
                file_object,
                path,
            )

        return file_object

    monkeypatch.setattr(
        Path,
        "open",
        recording_open,
    )

    with ThreadPoolExecutor(
        max_workers=2,
    ) as executor:
        futures = (
            executor.submit(
                first_publisher.publish_health,
                make_health(
                    cycle_count=1,
                ),
            ),
            executor.submit(
                second_publisher.publish_health,
                make_health(
                    cycle_count=2,
                ),
            ),
        )

        for future in futures:
            future.result()

    assert len(
        recorded_paths
    ) == 2

    assert len(
        set(
            recorded_paths
        )
    ) == 2

    for temporary_path in recorded_paths:
        assert temporary_path.parent == tmp_path
        assert temporary_path.name.startswith(
            ".dashboard.json."
        )
        assert temporary_path.name.endswith(
            ".tmp"
        )
        assert temporary_path.exists() is False

    assert dashboard_temporary_files(
        tmp_path
    ) == []

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload[
        "completed_cycle_count"
    ] in {
        1,
        2,
    }

def test_temporary_path_collision_does_not_overwrite_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    collided_path = (
        tmp_path
        / ".dashboard.json.collision.tmp"
    )
    collided_path.write_text(
        "existing temporary content",
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    generated_paths = iter(
        (
            collided_path,
            (
                tmp_path
                / ".dashboard.json.recovery.tmp"
            ),
        )
    )

    monkeypatch.setattr(
        publisher,
        "_build_temporary_path",
        lambda: next(
            generated_paths
        ),
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    assert collided_path.read_text(
        encoding="utf-8",
    ) == "existing temporary content"

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload[
        "completed_cycle_count"
    ] == 1

    collided_path.unlink()

def test_temporary_path_reservation_retries_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    collided_path = (
        tmp_path
        / ".dashboard.json.collision.tmp"
    )
    recovery_path = (
        tmp_path
        / ".dashboard.json.recovery.tmp"
    )

    collided_path.write_text(
        "occupied",
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    generated_paths: list[Path] = []

    def build_temporary_path() -> Path:
        path = (
            collided_path
            if not generated_paths
            else recovery_path
        )

        generated_paths.append(
            path
        )

        return path

    monkeypatch.setattr(
        publisher,
        "_build_temporary_path",
        build_temporary_path,
    )

    publisher.publish_health(
        make_health()
    )

    assert generated_paths == [
        collided_path,
        recovery_path,
    ]

    assert collided_path.read_text(
        encoding="utf-8",
    ) == "occupied"

    assert recovery_path.exists() is False
    assert output_path.exists()

    collided_path.unlink()

def test_temporary_path_reservation_raises_after_collision_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    collided_path = (
        tmp_path
        / ".dashboard.json.collision.tmp"
    )

    collided_path.write_text(
        "occupied",
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    build_attempts = 0

    def build_temporary_path() -> Path:
        nonlocal build_attempts

        build_attempts += 1

        return collided_path

    monkeypatch.setattr(
        publisher,
        "_build_temporary_path",
        build_temporary_path,
    )

    with pytest.raises(
        FileExistsError,
    ):
        publisher.publish_health(
            make_health()
        )

    assert (
        build_attempts
        == publisher._TEMPORARY_PATH_MAX_ATTEMPTS
    )

    assert collided_path.read_text(
        encoding="utf-8",
    ) == "occupied"

    assert output_path.exists() is False

    collided_path.unlink()

def test_temporary_payload_is_written_with_exclusive_mode(
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

    open_calls: list[
        tuple[Path, str, str | None, str | None]
    ] = []
    original_open = Path.open

    def recording_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        if is_dashboard_temporary_path(
            path,
            tmp_path,
        ):
            open_calls.append(
                (
                    path,
                    mode,
                    encoding,
                    newline,
                )
            )

        return original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "open",
        recording_open,
    )

    publisher.publish_health(
        make_health()
    )

    assert len(open_calls) == 1

    temporary_path, mode, encoding, newline = (
        open_calls[0]
    )

    assert mode == "x"
    assert encoding == "utf-8"
    assert newline == ""
    assert temporary_path.exists() is False

def test_exclusive_temporary_write_does_not_truncate_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )
    collided_path = (
        tmp_path
        / ".dashboard.json.collision.tmp"
    )
    recovery_path = (
        tmp_path
        / ".dashboard.json.recovery.tmp"
    )

    collided_path.write_text(
        "occupied",
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    generated_paths = iter(
        (
            collided_path,
            recovery_path,
        )
    )

    monkeypatch.setattr(
        publisher,
        "_build_temporary_path",
        lambda: next(
            generated_paths
        ),
    )

    publisher.publish_health(
        make_health(
            cycle_count=1,
        )
    )

    assert collided_path.read_text(
        encoding="utf-8",
    ) == "occupied"

    assert recovery_path.exists() is False
    assert output_path.exists()

    collided_path.unlink()

def test_exclusive_temporary_write_failure_creates_no_dashboard(
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

    original_open = Path.open

    def failing_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ):
        if (
            mode == "x"
            and is_dashboard_temporary_path(
                path,
                tmp_path,
            )
        ):
            raise PermissionError(
                "Dashboard directory is read-only."
            )

        return original_open(
            path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    monkeypatch.setattr(
        Path,
        "open",
        failing_open,
    )

    with pytest.raises(
        PermissionError,
        match="read-only",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.exists() is False
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_temporary_payload_is_flushed_before_atomic_replace(
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

    events: list[str] = []
    original_fsync = os.fsync
    original_replace = os.replace

    def recording_fsync(
        file_descriptor: int,
    ) -> None:
        events.append(
            "fsync"
        )

        original_fsync(
            file_descriptor
        )

    def recording_replace(
        source: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        destination: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    ) -> None:
        events.append(
            "replace"
        )

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "fsync",
        recording_fsync,
    )
    monkeypatch.setattr(
        os,
        "replace",
        recording_replace,
    )

    publisher.publish_health(
        make_health()
    )

    assert events == [
        "fsync",
        "replace",
    ]

    assert output_path.exists()
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_fsync_failure_preserves_existing_dashboard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = (
        tmp_path
        / "dashboard.json"
    )

    existing_payload = (
        '{"existing": true}\n'
    )

    output_path.write_text(
        existing_payload,
        encoding="utf-8",
    )

    publisher = DashboardStatusFilePublisher(
        path=output_path,
        symbol="NVDA",
        timeframe="2m",
    )

    def failing_fsync(
        file_descriptor: int,
    ) -> None:
        del file_descriptor

        raise OSError(
            "Temporary dashboard flush failed."
        )

    monkeypatch.setattr(
        os,
        "fsync",
        failing_fsync,
    )

    with pytest.raises(
        OSError,
        match="Temporary dashboard flush failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.read_text(
        encoding="utf-8",
    ) == existing_payload

    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_fsync_failure_creates_no_dashboard(
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

    def failing_fsync(
        file_descriptor: int,
    ) -> None:
        del file_descriptor

        raise OSError(
            "Temporary dashboard flush failed."
        )

    monkeypatch.setattr(
        os,
        "fsync",
        failing_fsync,
    )

    with pytest.raises(
        OSError,
        match="Temporary dashboard flush failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert output_path.exists() is False

    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_atomic_replace_skips_directory_fsync_when_unsupported(
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

    directory_opened = False
    original_open = os.open

    def recording_open(
        path,
        flags: int,
        mode: int = 0o777,
    ) -> int:
        nonlocal directory_opened

        if Path(path) == tmp_path:
            directory_opened = True

        return original_open(
            path,
            flags,
            mode,
        )

    monkeypatch.setattr(
        publisher,
        "_supports_directory_fsync",
        lambda: False,
    )
    monkeypatch.setattr(
        os,
        "open",
        recording_open,
    )

    publisher.publish_health(
        make_health()
    )

    assert directory_opened is False
    assert output_path.exists()

def test_parent_directory_is_synced_after_atomic_replace(
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

    events: list[str] = []
    directory_descriptor = 12345

    original_replace = os.replace
    original_fsync = os.fsync

    def recording_replace(
        source,
        destination,
    ) -> None:
        events.append(
            "replace"
        )

        original_replace(
            source,
            destination,
        )

    def recording_open(
        path,
        flags: int,
        mode: int = 0o777,
    ) -> int:
        assert Path(path) == tmp_path
        assert flags == os.O_RDONLY

        events.append(
            "directory-open"
        )

        return directory_descriptor

    def recording_fsync(
        file_descriptor: int,
    ) -> None:
        if file_descriptor == directory_descriptor:
            events.append(
                "directory-fsync"
            )
            return

        events.append(
            "file-fsync"
        )

        original_fsync(
            file_descriptor
        )

    def recording_close(
        file_descriptor: int,
    ) -> None:
        assert (
            file_descriptor
            == directory_descriptor
        )

        events.append(
            "directory-close"
        )

    monkeypatch.setattr(
        publisher,
        "_supports_directory_fsync",
        lambda: True,
    )
    monkeypatch.setattr(
        os,
        "replace",
        recording_replace,
    )
    monkeypatch.setattr(
        os,
        "open",
        recording_open,
    )
    monkeypatch.setattr(
        os,
        "fsync",
        recording_fsync,
    )
    monkeypatch.setattr(
        os,
        "close",
        recording_close,
    )

    publisher.publish_health(
        make_health()
    )

    assert events == [
        "file-fsync",
        "replace",
        "directory-open",
        "directory-fsync",
        "directory-close",
    ]

def test_parent_directory_descriptor_closes_when_fsync_fails(
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

    directory_descriptor = 12345
    closed_descriptors: list[int] = []
    original_fsync = os.fsync

    monkeypatch.setattr(
        publisher,
        "_supports_directory_fsync",
        lambda: True,
    )
    monkeypatch.setattr(
        os,
        "open",
        lambda path, flags: directory_descriptor,
    )

    def failing_directory_fsync(
        file_descriptor: int,
    ) -> None:
        if file_descriptor == directory_descriptor:
            raise OSError(
                "Directory sync failed."
            )

        original_fsync(
            file_descriptor
        )

    monkeypatch.setattr(
        os,
        "fsync",
        failing_directory_fsync,
    )
    monkeypatch.setattr(
        os,
        "close",
        lambda file_descriptor: (
            closed_descriptors.append(
                file_descriptor
            )
        ),
    )

    with pytest.raises(
        OSError,
        match="Directory sync failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert closed_descriptors == [
        directory_descriptor
    ]

    # Replacement completed before directory sync failed.
    assert output_path.exists()
    assert dashboard_temporary_files(
        tmp_path
    ) == []

def test_directory_fsync_failure_does_not_retry_replace(
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

    replace_count = 0
    original_replace = os.replace

    def recording_replace(
        source,
        destination,
    ) -> None:
        nonlocal replace_count

        replace_count += 1

        original_replace(
            source,
            destination,
        )

    monkeypatch.setattr(
        os,
        "replace",
        recording_replace,
    )
    monkeypatch.setattr(
        publisher,
        "_sync_parent_directory",
        lambda: (
            _raise_directory_sync_error()
        ),
    )

    with pytest.raises(
        PermissionError,
        match="Directory sync failed",
    ):
        publisher.publish_health(
            make_health()
        )

    assert replace_count == 1
    assert output_path.exists()