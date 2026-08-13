from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    BrokerPositionProtectionValidator,
    ExistingPositionProtectionPlanBuilder,
    ExistingPositionProtectionService,
)
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionOrderIntent,
    ExecutionPosition,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


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
        last_updated_at=NOW - timedelta(seconds=10),
        processed_fill_ids=("fill-1",),
    )


def plan(current=None):
    current = current or position()
    return ExistingPositionProtectionPlanBuilder().build(
        intent=ExecutionOrderIntent(
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
        ),
        position=current,
        coverage=ProtectiveCoverageAssessment(
            broker="alpaca-paper",
            symbol="NVDA",
            status=ProtectiveCoverageStatus.READY,
            position_quantity=40,
            protected_quantity=0,
            uncovered_quantity=40,
            actionable=True,
            reasons=("Protection required.",),
        ),
    )


def broker_position(**overrides):
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "direction": PositionDirection.LONG,
        "quantity": 40,
        "average_entry_price": 200.0,
        "market_price": 201.0,
        "unrealized_pnl": 40.0,
        "observed_at": NOW,
    }
    values.update(overrides)
    return BrokerPositionSnapshot(**values)


def accepted_result(plan_value):
    return ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=40,
        requested_quantity=40,
        accepted_quantity=40,
        position_updated_at=plan_value.position_updated_at,
        accepted=True,
        status="accepted",
        message="accepted",
        submissions=(
            ExistingPositionProtectionSubmission(
                label="target1",
                quantity=20,
                accepted=True,
                target_order_id="target-1",
                stop_order_id="stop-1",
                status="accepted",
                message="accepted",
            ),
            ExistingPositionProtectionSubmission(
                label="target2",
                quantity=20,
                accepted=True,
                target_order_id="target-2",
                stop_order_id="stop-2",
                status="accepted",
                message="accepted",
            ),
        ),
    )


class Store:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def get(self, *, broker, symbol):
        self.calls.append((broker, symbol))
        return self.value

    def save(self, position):
        self.value = position


class Query:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def get_position(self, symbol):
        self.calls.append(symbol)
        return self.value


class Protection:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def submit_existing_position_protection(self, *, plan, current_position):
        self.calls.append((plan, current_position))
        return self.result


def service(store, query, protection):
    return ExistingPositionProtectionService(
        position_store=store,
        position_query_port=query,
        protection_port=protection,
        validator=BrokerPositionProtectionValidator(clock=lambda: NOW),
    )


def test_service_validates_two_truths_then_submits_once():
    current = position()
    plan_value = plan(current)
    store = Store(current)
    query = Query(broker_position())
    protection = Protection(accepted_result(plan_value))

    result = service(store, query, protection).protect(plan_value)

    assert result.accepted is True
    assert store.calls == [("alpaca-paper", "NVDA")]
    assert query.calls == ["NVDA"]
    assert protection.calls == [(plan_value, current)]


def test_missing_persisted_position_fails_before_broker_query():
    query = Query(broker_position())
    protection = Protection(None)

    with pytest.raises(LookupError, match="No persisted position"):
        service(Store(None), query, protection).protect(plan())

    assert query.calls == []
    assert protection.calls == []


@pytest.mark.parametrize(
    "broker_truth",
    [None, broker_position(quantity=39), broker_position(observed_at=NOW - timedelta(seconds=6))],
)
def test_missing_mismatched_or_stale_broker_truth_blocks_submission(broker_truth):
    protection = Protection(None)

    with pytest.raises(ValueError):
        service(Store(position()), Query(broker_truth), protection).protect(plan())

    assert protection.calls == []


def test_changed_persisted_position_blocks_submission():
    protection = Protection(None)
    changed = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=39,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=position().last_updated_at,
        processed_fill_ids=("fill-1",),
    )

    with pytest.raises(ValueError, match="quantity"):
        service(Store(changed), Query(broker_position(quantity=39)), protection).protect(plan())

    assert protection.calls == []
