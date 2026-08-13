import pytest

from imie.models import (
    ProtectedOrderSubmission,
    ProtectedPlanSubmissionResult,
)


def make_submission(
    **overrides: object,
) -> ProtectedOrderSubmission:
    values = {
        "label": "target1",
        "quantity": 50,
        "accepted": True,
        "broker_order_id": "order-1",
        "status": "accepted",
        "message": "Accepted.",
    }
    values.update(overrides)
    return ProtectedOrderSubmission(**values)


def test_complete_result_requires_all_planned_quantity() -> None:
    result = ProtectedPlanSubmissionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        side="buy",
        quantity=100,
        accepted=True,
        status="accepted",
        message="Accepted.",
        submissions=(
            make_submission(),
            make_submission(
                label="target2",
                broker_order_id="order-2",
            ),
        ),
    )

    assert result.accepted is True
    assert len(result.submissions) == 2
    assert result.rollback_attempted is False
    assert result.rollback_succeeded is None


def test_partial_result_can_record_successful_rollback() -> None:
    result = ProtectedPlanSubmissionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        side="buy",
        quantity=100,
        accepted=False,
        status="rolled_back",
        message="Rolled back.",
        submissions=(
            make_submission(),
            make_submission(
                label="target2",
                accepted=False,
                broker_order_id=None,
                status="rejected",
            ),
        ),
        rollback_attempted=True,
        rollback_succeeded=True,
        rolled_back_order_ids=("order-1",),
    )

    assert result.rollback_succeeded is True
    assert result.rolled_back_order_ids == ("order-1",)


def test_accepted_slice_requires_order_id() -> None:
    with pytest.raises(ValueError, match="broker_order_id"):
        make_submission(broker_order_id=None)


def test_accepted_plan_rejects_incomplete_quantity() -> None:
    with pytest.raises(ValueError, match="every planned slice"):
        ProtectedPlanSubmissionResult(
            broker="alpaca-paper",
            symbol="NVDA",
            side="buy",
            quantity=100,
            accepted=True,
            status="accepted",
            message="Accepted.",
            submissions=(make_submission(),),
        )


def test_rollback_result_requires_attempt() -> None:
    with pytest.raises(ValueError, match="rollback_attempted"):
        ProtectedPlanSubmissionResult(
            broker="alpaca-paper",
            symbol="NVDA",
            side="buy",
            quantity=50,
            accepted=False,
            status="rejected",
            message="Rejected.",
            submissions=(
                make_submission(
                    accepted=False,
                    broker_order_id=None,
                    status="rejected",
                ),
            ),
            rollback_succeeded=True,
        )
