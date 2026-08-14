from datetime import datetime, timezone

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
)

from imie.models import (
    BrokerSubmissionResult,
    DailyLossAssessment,
    DecisionResult,
    DirectorDecision,
    ExecutionCandidate,
    ExecutionOrderIntent,
    PositionSizeResult,
    TradePlan,
)



def make_time(
    minute: int = 30,
) -> datetime:
    return datetime(
        2026,
        7,
        18,
        14,
        minute,
        tzinfo=timezone.utc,
    )

def make_decision_result() -> DecisionResult:
    return DecisionResult(
        decision=DirectorDecision.READY,
        actionable=True,
        confidence=90.0,
        recommendation="Ready.",
        reasons=(),
        warnings=(),
        analyst_summary={},
        trade_plan=make_trade_plan(),
        institutional_context=None,
    )

def make_position_size_result() -> PositionSizeResult:
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
    )

def make_broker_submission_result() -> BrokerSubmissionResult:
    return BrokerSubmissionResult(
        broker="mock",
        symbol="NVDA",
        side="buy",
        quantity=156,
        accepted=True,
        broker_order_id="mock-nvda-000001",
        status="accepted",
        message="Mock order accepted.",
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
    )

def make_trade_plan() -> TradePlan:
    return TradePlan(
        symbol="NVDA",
        strategy="Pullback-to-Core",
        direction="long",
        valid=True,
        actionable=True,
        decision="READY",
        entry=100.60,
        stop=99.80,
        target1=101.40,
        target2=102.20,
        risk_per_share=0.80,
        reward1_per_share=0.80,
        reward2_per_share=1.60,
        rr1=1.0,
        rr2=2.0,
        quality=90,
        confidence=90.0,
    )


def test_skipped_cycle_can_be_created() -> None:
    result = AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol=" nvda ",
        timeframe="2M",
        started_at=make_time(),
        completed_at=make_time(),
        message=" No new completed bar. ",
    )

    assert result.symbol == "NVDA"
    assert result.timeframe == "2m"
    assert result.message == "No new completed bar."
    assert result.succeeded is False
    assert result.skipped is True
    assert result.failed is False


def test_failed_cycle_requires_error_type() -> None:
    with pytest.raises(
        ValueError,
        match="error_type",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.FAILED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle failed.",
        )


def test_failed_cycle_is_identified() -> None:
    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.FAILED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Provider failed.",
        error_type=" RuntimeError ",
    )

    assert result.failed is True
    assert result.error_type == "RuntimeError"


def test_completed_cycle_requires_decision() -> None:
    with pytest.raises(
        ValueError,
        match="decision",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
        )


def test_stale_cycle_requires_freshness() -> None:
    with pytest.raises(
        ValueError,
        match="freshness",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.STALE_DATA,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Market data is stale.",
        )


def test_completion_cannot_precede_start() -> None:
    with pytest.raises(
        ValueError,
        match="completed_at",
    ):
        AnalysisCycleResult(
            status=(
                AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
            ),
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(
                minute=31,
            ),
            completed_at=make_time(
                minute=30,
            ),
            message="Skipped.",
        )


def test_timestamps_must_be_timezone_aware() -> None:
    with pytest.raises(
        ValueError,
        match="started_at",
    ):
        AnalysisCycleResult(
            status=(
                AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
            ),
            symbol="NVDA",
            timeframe="2m",
            started_at=datetime(
                2026,
                7,
                18,
                14,
                30,
            ),  # noqa: DTZ001
            completed_at=make_time(),
            message="Skipped.",
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "field_value",
    ),
    [
        (
            "symbol",
            " ",
        ),
        (
            "timeframe",
            "",
        ),
        (
            "message",
            " ",
        ),
    ],
)
def test_required_text_cannot_be_empty(
    field_name: str,
    field_value: str,
) -> None:
    arguments = {
        "status": (
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        "symbol": "NVDA",
        "timeframe": "2m",
        "started_at": make_time(),
        "completed_at": make_time(),
        "message": "Skipped.",
    }

    arguments[field_name] = field_value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AnalysisCycleResult(
            **arguments,  # type: ignore[arg-type]
        )

def test_completed_cycle_accepts_position_size_result() -> None:
    position_size = make_position_size_result()

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Cycle completed.",
        decision=make_decision_result(),
        position_size=position_size,
    )

    assert result.position_size is position_size

def test_rejects_invalid_position_size_type() -> None:
    with pytest.raises(
        TypeError,
        match="position_size must be a PositionSizeResult or None",
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            decision=make_decision_result(),
            position_size="invalid",  # type: ignore[arg-type]
        )

def test_completed_cycle_accepts_execution_candidate() -> None:
    execution_candidate = make_execution_candidate()

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Cycle completed.",
        decision=make_decision_result(),
        execution_candidate=execution_candidate,
    )

    assert (
        result.execution_candidate
        is execution_candidate
    )


def test_rejects_invalid_execution_candidate_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "execution_candidate must be an "
            "ExecutionCandidate or None"
        ),
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            decision=make_decision_result(),
            execution_candidate=(
                "invalid"  # type: ignore[arg-type]
            ),
        )


def test_completed_cycle_accepts_execution_order_intent() -> None:
    execution_order_intent = (
        make_execution_order_intent()
    )

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Cycle completed.",
        decision=make_decision_result(),
        execution_order_intent=(
            execution_order_intent
        ),
    )

    assert (
        result.execution_order_intent
        is execution_order_intent
    )


def test_rejects_invalid_execution_order_intent_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "execution_order_intent must be an "
            "ExecutionOrderIntent or None"
        ),
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            decision=make_decision_result(),
            execution_order_intent=(
                "invalid"  # type: ignore[arg-type]
            ),
        )

def test_completed_cycle_accepts_broker_submission_result() -> None:
    broker_submission_result = (
        make_broker_submission_result()
    )

    result = AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=make_time(),
        completed_at=make_time(),
        message="Cycle completed.",
        decision=make_decision_result(),
        broker_submission_result=(
            broker_submission_result
        ),
    )

    assert (
        result.broker_submission_result
        is broker_submission_result
    )


def test_rejects_invalid_broker_submission_result_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "broker_submission_result must be a "
            "BrokerSubmissionResult or None"
        ),
    ):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            decision=make_decision_result(),
            broker_submission_result=(
                "invalid"  # type: ignore[arg-type]
            ),
        )


def test_daily_loss_assessment_requires_execution_safety_assessment() -> None:
    daily_loss = DailyLossAssessment(
        broker="alpaca-paper", realized_pnl=-100, unrealized_pnl=-25,
        total_pnl=-125, loss_amount=125, maximum_daily_loss=500,
        within_limit=True, allowed=True,
    )

    with pytest.raises(ValueError, match="requires safety assessment"):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            daily_loss_assessment=daily_loss,
        )


def test_rejects_invalid_daily_loss_assessment_type() -> None:
    with pytest.raises(TypeError, match="daily_loss_assessment"):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=make_time(),
            completed_at=make_time(),
            message="Cycle completed.",
            daily_loss_assessment="invalid",  # type: ignore[arg-type]
        )
