from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest

from alpaca.trading.enums import OrderStatus, OrderType

from imie.execution import (
    AlpacaPaperExistingPositionProtectionAdapter,
    ExistingPositionProtectionPlanBuilder,
)
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)
PARENT_1 = UUID("11111111-1111-1111-1111-111111111111")
PARENT_2 = UUID("22222222-2222-2222-2222-222222222222")


def position():
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def plan(current=None):
    current = current or position()
    intent = ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=40,
        order_type="limit",
        entry_price=200.0,
        stop_price=199.0,
        target1_price=201.0,
        target2_price=202.0,
        time_in_force="gtc",
        valid=True,
        actionable=True,
    )
    coverage = ProtectiveCoverageAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        status=ProtectiveCoverageStatus.READY,
        position_quantity=40,
        protected_quantity=0,
        uncovered_quantity=40,
        actionable=True,
        reasons=("Protection required.",),
    )
    return ExistingPositionProtectionPlanBuilder().build(
        intent=intent, position=current, coverage=coverage
    )


def order(parent_id, *, status=OrderStatus.ACCEPTED, complete=True):
    legs = (
        [
            SimpleNamespace(id=f"target-{parent_id}", type=OrderType.LIMIT),
            SimpleNamespace(id=f"stop-{parent_id}", type=OrderType.STOP),
        ]
        if complete
        else []
    )
    return SimpleNamespace(id=parent_id, status=status, legs=legs)


class Client:
    def __init__(self, outcomes, *, cancel_error=None):
        self.outcomes = outcomes
        self.cancel_error = cancel_error
        self.requests = []
        self.cancelled = []

    def submit_order(self, order_data):
        self.requests.append(order_data)
        outcome = self.outcomes[len(self.requests) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def cancel_order_by_id(self, order_id):
        if self.cancel_error is not None:
            raise self.cancel_error
        self.cancelled.append(order_id)


def adapter(client, *, paper=True):
    return AlpacaPaperExistingPositionProtectionAdapter(
        trading_client=client, paper=paper
    )


def test_all_oco_slices_are_accepted_with_distinct_leg_ids():
    client = Client([order(PARENT_1), order(PARENT_2)])
    result = adapter(client).submit_existing_position_protection(
        plan=plan(), current_position=position()
    )

    assert result.accepted is True
    assert result.accepted_quantity == 40
    assert tuple(item.target_order_id for item in result.submissions) == (
        f"target-{PARENT_1}", f"target-{PARENT_2}"
    )
    assert tuple(item.stop_order_id for item in result.submissions) == (
        f"stop-{PARENT_1}", f"stop-{PARENT_2}"
    )
    assert client.cancelled == []


def test_second_failure_cancels_first_parent_oco():
    client = Client([order(PARENT_1), RuntimeError("endpoint unavailable")])
    result = adapter(client).submit_existing_position_protection(
        plan=plan(), current_position=position()
    )

    assert result.accepted is False
    assert result.status == "rolled_back"
    assert result.rollback_succeeded is True
    assert result.accepted_quantity == 20
    assert client.cancelled == [str(PARENT_1)]


def test_incomplete_accepted_response_is_canceled_and_not_reported_safe():
    client = Client([order(PARENT_1, complete=False), order(PARENT_2)])
    result = adapter(client).submit_existing_position_protection(
        plan=plan(), current_position=position()
    )

    assert result.accepted is False
    assert result.status == "rolled_back"
    assert result.accepted_quantity == 0
    assert result.submissions[0].status == "incomplete"
    assert result.submissions[1].status == "not_attempted"
    assert client.cancelled == [str(PARENT_1)]
    assert len(client.requests) == 1


def test_rollback_failure_is_visible():
    client = Client(
        [order(PARENT_1), RuntimeError("submit failed")],
        cancel_error=RuntimeError("cancel denied"),
    )
    result = adapter(client).submit_existing_position_protection(
        plan=plan(), current_position=position()
    )

    assert result.status == "rollback_failed"
    assert result.rollback_succeeded is False
    assert any("cancel denied" in warning for warning in result.warnings)


def test_changed_position_fails_before_any_submission():
    client = Client([order(PARENT_1), order(PARENT_2)])
    changed = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=39,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )

    with pytest.raises(ValueError, match="quantity"):
        adapter(client).submit_existing_position_protection(
            plan=plan(), current_position=changed
        )
    assert client.requests == []


def test_explicit_paper_gate_cannot_be_disabled():
    with pytest.raises(ValueError, match="paper-only"):
        adapter(Client([]), paper=False)


def test_cancel_support_is_required_at_construction():
    class SubmitOnly:
        def submit_order(self, order_data):
            return order(PARENT_1)

    with pytest.raises(TypeError, match="cancel_order_by_id"):
        adapter(SubmitOnly())
