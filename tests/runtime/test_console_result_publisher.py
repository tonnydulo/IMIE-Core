from datetime import datetime, timezone

from zoneinfo import ZoneInfo

import pytest

from imie.models import (
    DecisionResult,
    DirectorDecision,
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

