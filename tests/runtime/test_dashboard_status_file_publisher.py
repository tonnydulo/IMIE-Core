import json

from datetime import (
    datetime,
    timedelta,
    timezone,
)
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
        },
        trade_plan=trade_plan,
        institutional_context=(
        institutional_context
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