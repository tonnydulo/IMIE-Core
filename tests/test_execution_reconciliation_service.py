from datetime import datetime, timezone

import pytest

from imie.execution import ExecutionReconciliationService
from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    ExecutionOrderIntent,
)


NOW = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


def make_intent() -> ExecutionOrderIntent:
    return ExecutionOrderIntent(
        symbol="NVDA",
        side="buy",
        quantity=100,
        order_type="limit",
        entry_price=201.0,
        stop_price=200.0,
        target1_price=202.0,
        target2_price=203.0,
        time_in_force="day",
        valid=True,
        actionable=True,
    )


def make_snapshot(order_id: str = "order-123") -> BrokerOrderSnapshot:
    return BrokerOrderSnapshot(
        broker="fake",
        broker_order_id=order_id,
        symbol="NVDA",
        side="buy",
        order_type="limit",
        status=BrokerOrderStatus.PARTIALLY_FILLED,
        requested_quantity=100,
        filled_quantity=40,
        remaining_quantity=60,
        average_fill_price=201.25,
        submitted_at=NOW,
        accepted_at=NOW,
        last_updated_at=NOW,
    )


def make_fill() -> BrokerFill:
    return BrokerFill(
        broker="fake",
        broker_order_id="order-123",
        fill_id="fill-1",
        symbol="NVDA",
        side="buy",
        quantity=40,
        price=201.25,
        executed_at=NOW,
    )


class RecordingQueryPort:
    def __init__(
        self,
        *,
        snapshot: object | None = None,
        fills: object | None = None,
    ) -> None:
        self.snapshot = snapshot if snapshot is not None else make_snapshot()
        self.fills = fills if fills is not None else (make_fill(),)
        self.calls: list[tuple[str, str]] = []

    def get_order_snapshot(self, broker_order_id: str):
        self.calls.append(("snapshot", broker_order_id))
        return self.snapshot

    def get_order_fills(self, broker_order_id: str):
        self.calls.append(("fills", broker_order_id))
        return self.fills


def test_service_queries_once_and_reconciles() -> None:
    query_port = RecordingQueryPort()
    service = ExecutionReconciliationService(query_port=query_port)

    result = service.reconcile_order(
        intent=make_intent(),
        broker_order_id=" order-123 ",
    )

    assert result.reconciled is True
    assert query_port.calls == [
        ("snapshot", "order-123"),
        ("fills", "order-123"),
    ]


def test_unreconciled_result_is_returned_without_retry() -> None:
    query_port = RecordingQueryPort(fills=())

    result = ExecutionReconciliationService(
        query_port=query_port
    ).reconcile_order(
        intent=make_intent(),
        broker_order_id="order-123",
    )

    assert result.reconciled is False
    assert len(query_port.calls) == 2


def test_snapshot_order_id_mismatch_fails_before_fill_query() -> None:
    query_port = RecordingQueryPort(snapshot=make_snapshot("different-order"))

    with pytest.raises(ValueError, match="does not match"):
        ExecutionReconciliationService(
            query_port=query_port
        ).reconcile_order(
            intent=make_intent(),
            broker_order_id="order-123",
        )

    assert query_port.calls == [("snapshot", "order-123")]


def test_snapshot_return_type_is_validated() -> None:
    query_port = RecordingQueryPort(snapshot="not-a-snapshot")

    with pytest.raises(TypeError, match="BrokerOrderSnapshot"):
        ExecutionReconciliationService(
            query_port=query_port
        ).reconcile_order(
            intent=make_intent(),
            broker_order_id="order-123",
        )


class IncompleteQueryPort:
    def get_order_snapshot(self, broker_order_id: str):
        return make_snapshot()


def test_query_port_contract_is_required() -> None:
    with pytest.raises(TypeError, match="BrokerOrderQueryPort"):
        ExecutionReconciliationService(
            query_port=IncompleteQueryPort(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("value", "exception"),
    [
        ("", ValueError),
        ("   ", ValueError),
        (None, TypeError),
    ],
)
def test_broker_order_id_is_required(
    value: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception, match="broker_order_id"):
        ExecutionReconciliationService(
            query_port=RecordingQueryPort()
        ).reconcile_order(
            intent=make_intent(),
            broker_order_id=value,  # type: ignore[arg-type]
        )


def test_query_error_propagates_without_retry() -> None:
    class FailingQueryPort(RecordingQueryPort):
        def get_order_snapshot(self, broker_order_id: str):
            self.calls.append(("snapshot", broker_order_id))
            raise RuntimeError("broker unavailable")

    query_port = FailingQueryPort()

    with pytest.raises(RuntimeError, match="broker unavailable"):
        ExecutionReconciliationService(
            query_port=query_port
        ).reconcile_order(
            intent=make_intent(),
            broker_order_id="order-123",
        )

    assert query_port.calls == [("snapshot", "order-123")]

