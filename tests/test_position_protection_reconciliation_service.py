from datetime import datetime, timezone

import pytest

from imie.execution import PositionProtectionReconciliationService
from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    ExecutionPosition,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
    PositionDirection,
    PositionProtectionRecord,
)


NOW = datetime(2026, 8, 14, 0, 0, tzinfo=timezone.utc)


def position(quantity=5):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG if quantity else PositionDirection.FLAT,
        quantity=quantity,
        average_entry_price=200.0 if quantity else None,
        market_price=201.0,
        unrealized_pnl=5.0 if quantity else 0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def submission(label, quantity, suffix):
    return ExistingPositionProtectionSubmission(
        label=label,
        quantity=quantity,
        accepted=True,
        target_order_id=f"target-{suffix}",
        stop_order_id=f"stop-{suffix}",
        status="accepted",
        message="Accepted.",
    )


def record():
    result = ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=5,
        requested_quantity=5,
        accepted_quantity=5,
        position_updated_at=NOW,
        accepted=True,
        status="accepted",
        message="Accepted.",
        submissions=(submission("target1", 3, 1), submission("target2", 2, 2)),
    )
    return PositionProtectionRecord(
        result=result,
        position_fill_ids=("fill-1",),
        recorded_at=NOW,
    )


def snapshot(order_id):
    quantity = 3 if order_id.endswith("1") else 2
    return BrokerOrderSnapshot(
        broker="alpaca-paper",
        broker_order_id=order_id,
        symbol="NVDA",
        side="sell",
        order_type="limit" if order_id.startswith("target") else "stop",
        status=BrokerOrderStatus.ACCEPTED,
        requested_quantity=quantity,
        filled_quantity=0,
        remaining_quantity=quantity,
        last_updated_at=NOW,
    )


class PositionStore:
    def __init__(self, value):
        self.value = value

    def save(self, value):
        self.value = value

    def get(self, **kwargs):
        return self.value


class ProtectionStore:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def save(self, value):
        self.value = value

    def get_for_position(self, **kwargs):
        self.calls.append(kwargs)
        return self.value


class QueryPort:
    def __init__(self):
        self.calls = []

    def get_order_snapshot(self, order_id):
        self.calls.append(("snapshot", order_id))
        return snapshot(order_id)

    def get_order_fills(self, order_id):
        self.calls.append(("fills", order_id))
        return ()


def service(position_value=None, record_value=None, query=None):
    return PositionProtectionReconciliationService(
        position_store=PositionStore(position_value),
        protection_store=ProtectionStore(record_value),
        query_port=query or QueryPort(),
    )


def test_queries_each_recorded_protective_order_once_without_fills():
    query = QueryPort()
    result = service(position(), record(), query).reconcile(
        broker="alpaca-paper", symbol="NVDA"
    )

    assert result.state == "active"
    assert query.calls == [
        ("snapshot", "target-1"),
        ("snapshot", "stop-1"),
        ("snapshot", "target-2"),
        ("snapshot", "stop-2"),
    ]


@pytest.mark.parametrize(
    "position_value, record_value, message",
    [
        (None, None, "No reconciled position"),
        (position(0), None, "flat position"),
        (position(), None, "No accepted protection record"),
    ],
)
def test_missing_local_truth_fails_before_broker_query(
    position_value, record_value, message
):
    query = QueryPort()

    with pytest.raises((LookupError, ValueError), match=message):
        service(position_value, record_value, query).reconcile(
            broker="alpaca-paper", symbol="NVDA"
        )

    assert query.calls == []


def test_snapshot_id_mismatch_fails_without_querying_remaining_orders():
    class WrongIdQuery(QueryPort):
        def get_order_snapshot(self, order_id):
            self.calls.append(("snapshot", order_id))
            return snapshot("wrong-id")

    query = WrongIdQuery()
    with pytest.raises(ValueError, match="does not match"):
        service(position(), record(), query).reconcile(
            broker="alpaca-paper", symbol="NVDA"
        )

    assert query.calls == [("snapshot", "target-1")]
