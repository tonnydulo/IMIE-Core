from datetime import datetime, timezone

import pytest

from imie.execution import ProtectedExecutionPort
from imie.models import (
    DecisionResult,
    DirectorDecision,
    ProtectedExecutionPlan,
    ProtectedOrderSubmission,
    ProtectedPlanSubmissionResult,
)
from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    ConsoleResultPublisher,
    JsonResultPublisher,
    RuntimeDashboardStatus,
    RuntimeHealthState,
    RuntimeHealthSummary,
)


CHECKED_AT = datetime(2026, 8, 13, 15, 30, tzinfo=timezone.utc)


def make_protected_result() -> ProtectedPlanSubmissionResult:
    return ProtectedPlanSubmissionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        side="buy",
        quantity=100,
        accepted=False,
        status="rolled_back",
        message="Partial protected submission was fully rolled back.",
        submissions=(
            ProtectedOrderSubmission(
                label="target1",
                quantity=50,
                accepted=True,
                broker_order_id="order-1",
                status="accepted",
                message="Accepted.",
            ),
            ProtectedOrderSubmission(
                label="target2",
                quantity=50,
                accepted=False,
                broker_order_id=None,
                status="rejected",
                message="Rejected.",
            ),
        ),
        rollback_attempted=True,
        rollback_succeeded=True,
        rolled_back_order_ids=("order-1",),
        warnings=("Second bracket rejected.",),
    )


def make_cycle_result() -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=AnalysisCycleStatus.COMPLETED,
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message="Completed.",
        decision=DecisionResult(
            decision=DirectorDecision.WAIT,
            actionable=False,
            confidence=50.0,
            recommendation="Wait.",
        ),
        protected_submission_result=make_protected_result(),
    )


def test_protected_execution_port_protocol() -> None:
    class FakePort:
        def submit_protected_plan(
            self,
            plan: ProtectedExecutionPlan,
        ) -> ProtectedPlanSubmissionResult:
            del plan
            return make_protected_result()

    port: ProtectedExecutionPort = FakePort()
    assert callable(port.submit_protected_plan)


def test_cycle_accepts_protected_submission_result() -> None:
    result = make_cycle_result()
    assert result.protected_submission_result is not None
    assert result.protected_submission_result.status == "rolled_back"


def test_cycle_rejects_both_submission_result_types() -> None:
    from imie.models import BrokerSubmissionResult

    with pytest.raises(ValueError, match="both single and protected"):
        AnalysisCycleResult(
            status=AnalysisCycleStatus.COMPLETED,
            symbol="NVDA",
            timeframe="2m",
            started_at=CHECKED_AT,
            completed_at=CHECKED_AT,
            message="Completed.",
            decision=make_cycle_result().decision,
            broker_submission_result=BrokerSubmissionResult(
                broker="mock",
                symbol="NVDA",
                side="buy",
                quantity=100,
                accepted=True,
                broker_order_id="mock-1",
                status="accepted",
                message="Accepted.",
            ),
            protected_submission_result=make_protected_result(),
        )


def test_json_publishes_protected_submission_details() -> None:
    payload = JsonResultPublisher(output=lambda value: None).to_dict(
        make_cycle_result()
    )
    protected = payload["protected_submission_result"]

    assert protected["status"] == "rolled_back"
    assert protected["rollback_succeeded"] is True
    assert protected["rolled_back_order_ids"] == ["order-1"]
    assert protected["submissions"][1]["label"] == "target2"
    assert protected["submissions"][1]["accepted"] is False


def test_console_publishes_protected_submission_summary() -> None:
    lines = ConsoleResultPublisher(output=lambda line: None).format_lines(
        make_cycle_result()
    )

    assert "Protected Submission Result :" in lines
    assert "Status           : rolled_back" in lines
    assert "Rollback Success : True" in lines
    assert any("target2: qty=50" in line for line in lines)


def test_dashboard_status_serializes_protected_summary() -> None:
    health = RuntimeHealthSummary(
        state=RuntimeHealthState.RUNNING,
        started_at=CHECKED_AT,
        checked_at=CHECKED_AT,
        uptime_seconds=0.0,
        last_transition_at=CHECKED_AT,
        last_heartbeat_at=None,
        last_successful_cycle_at=CHECKED_AT,
        completed_cycle_count=1,
        error_type=None,
    )
    status = RuntimeDashboardStatus(
        health=health,
        symbol="NVDA",
        timeframe="2m",
        latest_cycle_status=AnalysisCycleStatus.COMPLETED,
        latest_cycle_message="Completed.",
        latest_cycle_started_at=CHECKED_AT,
        latest_cycle_completed_at=CHECKED_AT,
        market_session="REGULAR",
        latest_decision="WAIT",
        latest_error_type=None,
        protected_submission_broker="alpaca-paper",
        protected_submission_quantity=100,
        protected_submission_accepted=False,
        protected_submission_status="rolled_back",
        protected_submission_message="Rolled back.",
        protected_submission_order_count=2,
        protected_submission_rollback_attempted=True,
        protected_submission_rollback_succeeded=True,
        protected_submission_warnings=("Second bracket rejected.",),
    )

    payload = status.to_dict()
    assert payload["protected_submission_broker"] == "alpaca-paper"
    assert payload["protected_submission_order_count"] == 2
    assert payload["protected_submission_rollback_succeeded"] is True
    assert payload["protected_submission_warnings"] == [
        "Second bracket rejected."
    ]
