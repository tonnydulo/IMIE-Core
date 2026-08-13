from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import PositionReconciliationService
from imie.models import BrokerFill, ExecutionPosition, PositionDirection


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def fill(fill_id="fill-1", *, seconds=0, **overrides):
    values = {
        "broker": "alpaca-paper",
        "broker_order_id": "order-123",
        "fill_id": fill_id,
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 40,
        "price": 200.0,
        "executed_at": NOW + timedelta(seconds=seconds),
    }
    values.update(overrides)
    return BrokerFill(**values)


class QueryPort:
    def __init__(self, fills=()):
        self.fills = fills
        self.calls = []

    def get_order_snapshot(self, broker_order_id):
        raise AssertionError("position reconciliation must not query snapshots")

    def get_order_fills(self, broker_order_id):
        self.calls.append(broker_order_id)
        return self.fills


class PositionStore:
    def __init__(self, position=None):
        self.position = position
        self.get_calls = []
        self.saved = []

    def get(self, *, broker, symbol):
        self.get_calls.append((broker, symbol))
        return self.position

    def save(self, position):
        self.saved.append(position)
        self.position = position


def existing(*, processed_fill_ids=("fill-1",), updated_at=NOW):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=40,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=updated_at,
        processed_fill_ids=processed_fill_ids,
    )


def test_first_fill_initializes_and_persists_position():
    query = QueryPort((fill(),))
    store = PositionStore()
    service = PositionReconciliationService(
        query_port=query, position_store=store
    )

    result = service.reconcile_order_position(
        broker=" ALPACA-PAPER ",
        broker_order_id=" order-123 ",
        symbol=" nvda ",
        market_price=201.0,
    )

    assert result.direction is PositionDirection.LONG
    assert result.quantity == 40
    assert result.unrealized_pnl == 40.0
    assert result.processed_fill_ids == ("fill-1",)
    assert store.saved == [result]
    assert store.get_calls == [("alpaca-paper", "NVDA")]
    assert query.calls == ["order-123"]


def test_complete_fill_history_only_applies_unseen_fill():
    current = existing()
    store = PositionStore(current)
    service = PositionReconciliationService(
        query_port=QueryPort(
            (fill(), fill("fill-2", seconds=1, quantity=10, price=202.0))
        ),
        position_store=store,
    )

    result = service.reconcile_order_position(
        broker="alpaca-paper", broker_order_id="order-123", symbol="NVDA"
    )

    assert result.quantity == 50
    assert result.average_entry_price == pytest.approx(200.4)
    assert result.processed_fill_ids == ("fill-1", "fill-2")
    assert store.saved == [result]


def test_repeated_reconciliation_is_idempotent_and_does_not_save():
    current = existing()
    store = PositionStore(current)
    service = PositionReconciliationService(
        query_port=QueryPort((fill(),)), position_store=store
    )

    result = service.reconcile_order_position(
        broker="alpaca-paper",
        broker_order_id="order-123",
        symbol="NVDA",
        market_price=250.0,
    )

    assert result is current
    assert store.saved == []


def test_no_position_and_no_fills_returns_none_without_save():
    store = PositionStore()
    service = PositionReconciliationService(
        query_port=QueryPort(), position_store=store
    )

    assert service.reconcile_order_position(
        broker="alpaca-paper", broker_order_id="order-123", symbol="NVDA"
    ) is None
    assert store.saved == []


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"broker": "other"}, "broker"),
        ({"broker_order_id": "other"}, "order ID"),
        ({"symbol": "AMD"}, "symbol"),
    ],
)
def test_mismatched_broker_fill_identity_is_rejected(overrides, message):
    service = PositionReconciliationService(
        query_port=QueryPort((fill(**overrides),)),
        position_store=PositionStore(),
    )

    with pytest.raises(ValueError, match=message):
        service.reconcile_order_position(
            broker="alpaca-paper",
            broker_order_id="order-123",
            symbol="NVDA",
        )


def test_query_port_must_return_fill_tuple():
    service = PositionReconciliationService(
        query_port=QueryPort([]), position_store=PositionStore()
    )

    with pytest.raises(TypeError, match="tuple of BrokerFill"):
        service.reconcile_order_position(
            broker="alpaca-paper", broker_order_id="order-123", symbol="NVDA"
        )
