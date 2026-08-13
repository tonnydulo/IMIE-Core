from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    BrokerPositionProtectionValidator,
    ExistingPositionProtectionPlanBuilder,
)
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def recorded(**overrides):
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "direction": PositionDirection.LONG,
        "quantity": 40,
        "average_entry_price": 200.0,
        "market_price": None,
        "unrealized_pnl": 0.0,
        "realized_pnl": 0.0,
        "last_updated_at": NOW - timedelta(seconds=10),
        "processed_fill_ids": ("fill-1",),
    }
    values.update(overrides)
    return ExecutionPosition(**values)


def plan(position=None):
    position = position or recorded()
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
        intent=intent, position=position, coverage=coverage
    )


def broker(**overrides):
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


def validator(**overrides):
    return BrokerPositionProtectionValidator(
        clock=lambda: NOW,
        **overrides,
    )


def test_fresh_matching_broker_truth_returns_guarded_position():
    position = recorded()

    result = validator().validate(
        plan=plan(position),
        recorded_position=position,
        broker_position=broker(),
    )

    assert result is position


def test_small_average_entry_rounding_difference_is_allowed():
    validator().validate(
        plan=plan(),
        recorded_position=recorded(),
        broker_position=broker(average_entry_price=200.00009),
    )


def test_missing_broker_position_fails_closed():
    with pytest.raises(ValueError, match="no open position"):
        validator().validate(
            plan=plan(),
            recorded_position=recorded(),
            broker_position=None,
        )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"broker": "other"}, "broker"),
        ({"symbol": "AMD"}, "symbol"),
        ({"direction": PositionDirection.SHORT}, "direction"),
        ({"quantity": 39}, "quantity"),
        ({"average_entry_price": 200.01}, "average entry"),
    ],
)
def test_broker_truth_mismatch_fails_closed(overrides, message):
    with pytest.raises(ValueError, match=message):
        validator().validate(
            plan=plan(),
            recorded_position=recorded(),
            broker_position=broker(**overrides),
        )


def test_stale_broker_snapshot_is_rejected():
    with pytest.raises(ValueError, match="stale"):
        validator(maximum_snapshot_age=timedelta(seconds=5)).validate(
            plan=plan(),
            recorded_position=recorded(),
            broker_position=broker(observed_at=NOW - timedelta(seconds=6)),
        )


def test_future_broker_snapshot_is_rejected():
    with pytest.raises(ValueError, match="future"):
        validator().validate(
            plan=plan(),
            recorded_position=recorded(),
            broker_position=broker(observed_at=NOW + timedelta(microseconds=1)),
        )


def test_changed_recorded_position_is_rejected_before_broker_comparison():
    changed = recorded(quantity=39)

    with pytest.raises(ValueError, match="quantity"):
        validator().validate(
            plan=plan(),
            recorded_position=changed,
            broker_position=broker(quantity=39),
        )
