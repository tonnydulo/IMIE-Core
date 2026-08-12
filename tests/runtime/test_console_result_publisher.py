from datetime import datetime, timezone

from zoneinfo import ZoneInfo

import pytest

from imie.models import (
    DecisionResult,
    DirectorDecision,
    ExecutionCandidate,
    ExecutionOrderIntent,
    PositionSizeResult,
)
from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    ConsoleResultPublisher,
    MarketSessionResult,
    MarketSessionState,
    SessionPolicyAction,
    SessionPolicyResult,
)


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


def make_skipped_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="No new completed bar.",
    )


def make_failed_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.FAILED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Provider unavailable.",
        error_type="RuntimeError",
    )


def make_completed_result() -> AnalysisCycleResult:
    decision = DecisionResult(
        decision=DirectorDecision.PREPARE,
        actionable=False,
        confidence=82.5,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        reasons=(
            "Setup is developing.",
        ),
        warnings=(
            "Institutional conflict is present.",
        ),
    )

    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Analysis completed.",
        decision=decision,
    )

def make_position_size() -> PositionSizeResult:
    return PositionSizeResult(
        symbol="NVDA",
        direction="long",
        account_equity=25_000.0,
        risk_percent=0.50,
        risk_budget=125.0,
        entry=100.60,
        stop=99.80,
        risk_per_share=0.80,
        quantity=156,
        position_notional=15_693.60,
        actual_risk=124.80,
        actual_risk_percent=0.4992,
        valid=True,
        actionable=True,
        reasons=(
            "Position size calculated from account risk budget.",
        ),
        warnings=(),
    )

def make_execution_order_intent() -> ExecutionOrderIntent:
    return ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=156,
        order_type="limit",
        entry_price=100.60,
        stop_price=99.80,
        target1_price=101.40,
        target2_price=102.20,
        time_in_force="day",
        valid=True,
        actionable=True,
        reasons=(
            "Execution candidate converted to order intent.",
        ),
        warnings=(),
    )

def make_execution_candidate() -> ExecutionCandidate:
    return ExecutionCandidate(
        symbol="NVDA",
        strategy="Pullback-to-Core",
        direction="long",
        quantity=156,
        entry=100.60,
        stop=99.80,
        target1=101.40,
        target2=102.20,
        position_notional=15_693.60,
        risk_amount=124.80,
        valid=True,
        actionable=True,
        reasons=(
            "Trade plan and position size are approved.",
        ),
        warnings=(),
    )

def make_sized_completed_result() -> AnalysisCycleResult:
    decision = DecisionResult(
        decision=DirectorDecision.PREPARE,
        actionable=False,
        confidence=82.5,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        reasons=(
            "Setup is developing.",
        ),
        warnings=(
            "Institutional conflict is present.",
        ),
    )

    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Analysis completed.",
        decision=decision,
        position_size=make_position_size(),
        execution_candidate=(
            make_execution_candidate()
        ),
        execution_order_intent=(
            make_execution_order_intent()
        ),
    )

def test_sized_completed_result_includes_execution_candidate() -> None:
    publisher = ConsoleResultPublisher(
        output=lambda line: None,
    )

    lines = publisher.format_lines(
        make_sized_completed_result()
    )

    assert "Position Size :" in lines
    assert "Direction    : long" in lines
    assert "Risk Budget  : $125.00" in lines
    assert "Risk %       : 0.50%" in lines
    assert "Quantity     : 156" in lines
    assert "Notional     : $15693.60" in lines
    assert "Actual Risk  : $124.80" in lines
    assert "Actual Risk %: 0.4992%" in lines
    assert "Size Actionable: True" in lines

    assert "Execution Candidate :" in lines
    assert "Strategy     : Pullback-to-Core" in lines
    assert "Direction    : long" in lines
    assert "Quantity     : 156" in lines
    assert "Entry        : $100.60" in lines
    assert "Stop         : $99.80" in lines
    assert "Target 1     : $101.40" in lines
    assert "Target 2     : $102.20" in lines
    assert "Notional     : $15693.60" in lines
    assert "Risk Amount  : $124.80" in lines
    assert "Exec Valid   : True" in lines
    assert "Exec Actionable: True" in lines

    assert "Execution Order Intent :" in lines
    assert "Side         : buy" in lines
    assert "Quantity     : 156" in lines
    assert "Order Type   : limit" in lines
    assert "Entry Price  : $100.60" in lines
    assert "Stop Price   : $99.80" in lines
    assert "Target 1     : $101.40" in lines
    assert "Target 2     : $102.20" in lines
    assert "Time in Force: day" in lines
    assert "Order Valid  : True" in lines
    assert "Order Actionable: True" in lines

def test_publisher_can_be_created() -> None:
    lines: list[str] = []

    publisher = ConsoleResultPublisher(
        output=lines.append,
    )

    publisher.output(
    "test"
    )

    assert lines == [
        "test",
    ]


def test_output_must_be_callable() -> None:
    with pytest.raises(
        TypeError,
        match="output",
    ):
        ConsoleResultPublisher(
            output=object(),  # type: ignore[arg-type]
        )


def test_skipped_result_is_formatted() -> None:
    publisher = ConsoleResultPublisher(
        output=lambda line: None,
    )

    lines = publisher.format_lines(
        make_skipped_result()
    )

    assert "Status       : SKIPPED_NO_NEW_BAR" in lines
    assert "Symbol       : NVDA" in lines
    assert "Timeframe    : 2m" in lines
    assert "Message      : No new completed bar." in lines


def test_failed_result_includes_error_type() -> None:
    publisher = ConsoleResultPublisher(
        output=lambda line: None,
    )

    lines = publisher.format_lines(
        make_failed_result()
    )

    assert "Status       : FAILED" in lines
    assert "Error Type   : RuntimeError" in lines


def test_completed_result_includes_decision() -> None:
    publisher = ConsoleResultPublisher(
        output=lambda line: None,
    )

    lines = publisher.format_lines(
        make_completed_result()
    )

    assert "Status       : COMPLETED" in lines
    assert "Decision     : PREPARE" in lines
    assert "Actionable   : False" in lines
    assert "Confidence   : 82.5" in lines
    assert (
        "Recommendation: Prepare for a possible "
        "validated setup."
        in lines
    )
    assert "Reasons      :" in lines
    assert " - Setup is developing." in lines
    assert "Warnings     :" in lines
    assert " - Institutional conflict is present." in lines

    assert "Position Size :" not in lines
    assert "Execution Candidate :" not in lines
    assert "Execution Order Intent :" not in lines


def test_publish_sends_every_line_to_output() -> None:
    emitted: list[str] = []

    publisher = ConsoleResultPublisher(
        output=emitted.append,
    )

    result = make_failed_result()

    expected = publisher.format_lines(
        result
    )

    publisher.publish(
        result
    )

    assert emitted == list(
        expected
    )


def test_publisher_is_callable() -> None:
    emitted: list[str] = []

    publisher = ConsoleResultPublisher(
        output=emitted.append,
    )

    publisher(
        make_skipped_result()
    )

    assert emitted
    assert "Status       : SKIPPED_NO_NEW_BAR" in emitted


def test_result_must_be_analysis_cycle_result() -> None:
    publisher = ConsoleResultPublisher(
        output=lambda line: None,
    )

    with pytest.raises(
        TypeError,
        match="AnalysisCycleResult",
    ):
        publisher.publish(
            object(),  # type: ignore[arg-type]
        )

def test_publish_includes_market_session_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    checked_at = datetime(
        2026,
        7,
        19,
        16,
        9,
        tzinfo=timezone.utc,
    )

    market_session = MarketSessionResult(
        state=MarketSessionState.CLOSED,
        checked_at=checked_at,
        market_time=checked_at.astimezone(
            ZoneInfo(
                "America/New_York"
            )
        ),
        is_trading_day=False,
        reason="The market is closed.",
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
        status=AnalysisCycleStatus.SKIPPED_SESSION,
        symbol="NVDA",
        timeframe="2m",
        started_at=checked_at,
        completed_at=checked_at,
        message=session_policy.reason,
        market_session=market_session,
        session_policy=session_policy,
    )

    publisher = ConsoleResultPublisher()

    publisher.publish(
        result
    )

    rendered = capsys.readouterr().out

    assert "Session      : CLOSED" in rendered
    assert "Market Time  :" in rendered
    assert "Trading Day  : False" in rendered
    assert "Session Action: SKIP" in rendered
    assert (
        "Runtime analysis is disabled during "
        "the CLOSED session."
        in rendered
    )

