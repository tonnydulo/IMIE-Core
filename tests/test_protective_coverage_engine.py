from datetime import datetime, timezone

import pytest

from imie.execution import ProtectiveCoverageEngine
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectedOrderSubmission,
    ProtectedPlanSubmissionResult,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def intent(*, side="buy", symbol="NVDA", quantity=100):
    return ExecutionOrderIntent(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type="limit",
        entry_price=200.0,
        stop_price=199.0,
        target1_price=201.0,
        target2_price=202.0,
        time_in_force="day",
        valid=True,
        actionable=True,
    )


def position(
    *, direction=PositionDirection.LONG, quantity=40, symbol="NVDA"
):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol=symbol,
        direction=direction,
        quantity=quantity,
        average_entry_price=(200.0 if quantity else None),
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
    )


def submission(*, quantity=40, accepted=True, **overrides):
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "side": "buy",
        "quantity": quantity,
        "accepted": accepted,
        "status": "accepted" if accepted else "rejected",
        "message": "result",
        "submissions": (
            ProtectedOrderSubmission(
                label="target1",
                quantity=quantity,
                accepted=accepted,
                broker_order_id="order-1" if accepted else None,
                status="accepted" if accepted else "rejected",
                message="result",
            ),
        ),
    }
    values.update(overrides)
    return ProtectedPlanSubmissionResult(**values)


def test_no_position_is_not_actionable():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(), position=None
    )

    assert result.status is ProtectiveCoverageStatus.NO_POSITION
    assert result.actionable is False


def test_flat_position_requires_no_protection():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(),
        position=position(direction=PositionDirection.FLAT, quantity=0),
    )

    assert result.status is ProtectiveCoverageStatus.FLAT
    assert result.uncovered_quantity == 0


def test_open_unprotected_position_is_ready():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(), position=position()
    )

    assert result.status is ProtectiveCoverageStatus.READY
    assert result.position_quantity == 40
    assert result.protected_quantity == 0
    assert result.uncovered_quantity == 40
    assert result.actionable is True


def test_accepted_submission_covers_position():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(), position=position(), submission=submission()
    )

    assert result.status is ProtectiveCoverageStatus.PROTECTED
    assert result.protected_quantity == 40
    assert result.uncovered_quantity == 0
    assert result.actionable is False


def test_partial_coverage_reports_uncovered_quantity():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(),
        position=position(),
        submission=submission(quantity=25),
    )

    assert result.status is ProtectiveCoverageStatus.PARTIALLY_PROTECTED
    assert result.protected_quantity == 25
    assert result.uncovered_quantity == 15
    assert result.actionable is True


def test_rejected_submission_leaves_position_ready_with_warning():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(),
        position=position(),
        submission=submission(accepted=False),
    )

    assert result.status is ProtectiveCoverageStatus.READY
    assert result.warnings == (
        "The prior protected submission was not accepted.",
    )


def test_short_position_matches_sell_intent_and_submission():
    result = ProtectiveCoverageEngine().assess(
        intent=intent(side="sell"),
        position=position(direction=PositionDirection.SHORT),
        submission=submission(side="sell"),
    )

    assert result.status is ProtectiveCoverageStatus.PROTECTED


@pytest.mark.parametrize(
    ("intent_value", "position_value", "submission_value", "message"),
    [
        (intent(symbol="AMD"), position(), None, "Intent symbol"),
        (intent(side="sell"), position(), None, "Intent side"),
        (intent(quantity=20), position(), None, "exceeds planned"),
        (intent(), position(), submission(broker="other"), "broker"),
        (intent(), position(), submission(symbol="AMD"), "symbol"),
        (intent(), position(), submission(side="sell"), "side"),
    ],
)
def test_identity_or_planning_mismatch_blocks_action(
    intent_value, position_value, submission_value, message
):
    result = ProtectiveCoverageEngine().assess(
        intent=intent_value,
        position=position_value,
        submission=submission_value,
    )

    assert result.status is ProtectiveCoverageStatus.MISMATCH
    assert result.actionable is False
    assert any(message in reason for reason in result.reasons)
