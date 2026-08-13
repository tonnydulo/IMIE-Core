from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from alpaca.trading.enums import OrderSide, OrderStatus, OrderType

from imie.execution import (
    AlpacaPaperExecutionAdapter,
    BrokerOrderQueryPort,
)
from imie.models import BrokerOrderStatus


NOW = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


class QueryTradingClient:
    def __init__(self, order: object) -> None:
        self.order = order
        self.requested_order_ids: list[str] = []

    def submit_order(self, order_data: object) -> object:
        raise NotImplementedError

    def get_order_by_id(self, order_id: str) -> object:
        self.requested_order_ids.append(order_id)
        return self.order


class FillActivitySource:
    def __init__(self, activities: tuple[object, ...]) -> None:
        self.activities = activities
        self.requested_order_ids: list[str] = []

    def get_fill_activities(self, broker_order_id: str):
        self.requested_order_ids.append(broker_order_id)
        return self.activities


def alpaca_order(**overrides: object) -> object:
    values = {
        "id": "order-123",
        "client_order_id": "client-123",
        "symbol": "NVDA",
        "side": OrderSide.BUY,
        "order_type": OrderType.LIMIT,
        "status": OrderStatus.PARTIALLY_FILLED,
        "qty": "100",
        "filled_qty": "40",
        "filled_avg_price": "201.25",
        "created_at": NOW,
        "submitted_at": NOW,
        "updated_at": NOW + timedelta(seconds=2),
        "filled_at": None,
        "canceled_at": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_adapter(
    order: object,
    fill_source: FillActivitySource | None = None,
) -> AlpacaPaperExecutionAdapter:
    return AlpacaPaperExecutionAdapter(
        api_key="paper-key",
        secret_key="paper-secret",
        trading_client=QueryTradingClient(order),
        fill_activity_source=fill_source,
    )


def test_adapter_satisfies_order_query_port() -> None:
    adapter = make_adapter(alpaca_order())

    assert isinstance(adapter, BrokerOrderQueryPort)


def test_alpaca_order_is_translated_to_snapshot() -> None:
    adapter = make_adapter(alpaca_order())

    snapshot = adapter.get_order_snapshot(" order-123 ")

    assert snapshot.broker == "alpaca-paper"
    assert snapshot.broker_order_id == "order-123"
    assert snapshot.client_order_id == "client-123"
    assert snapshot.status is BrokerOrderStatus.PARTIALLY_FILLED
    assert snapshot.requested_quantity == 100
    assert snapshot.filled_quantity == 40
    assert snapshot.remaining_quantity == 60
    assert snapshot.average_fill_price == 201.25
    assert snapshot.last_updated_at == NOW + timedelta(seconds=2)


@pytest.mark.parametrize(
    ("alpaca_status", "expected"),
    [
        (OrderStatus.NEW, BrokerOrderStatus.SUBMITTED),
        (OrderStatus.ACCEPTED, BrokerOrderStatus.ACCEPTED),
        (OrderStatus.PARTIALLY_FILLED, BrokerOrderStatus.PARTIALLY_FILLED),
        (OrderStatus.FILLED, BrokerOrderStatus.FILLED),
        (OrderStatus.PENDING_CANCEL, BrokerOrderStatus.PENDING_CANCEL),
        (OrderStatus.CANCELED, BrokerOrderStatus.CANCELED),
        (OrderStatus.REJECTED, BrokerOrderStatus.REJECTED),
        (OrderStatus.EXPIRED, BrokerOrderStatus.EXPIRED),
        (OrderStatus.REPLACED, BrokerOrderStatus.REPLACED),
        (OrderStatus.SUSPENDED, BrokerOrderStatus.UNKNOWN),
    ],
)
def test_alpaca_status_mapping(alpaca_status, expected) -> None:
    filled = alpaca_status is OrderStatus.FILLED
    partial = alpaca_status is OrderStatus.PARTIALLY_FILLED
    snapshot = make_adapter(
        alpaca_order(
            status=alpaca_status,
            filled_qty="100" if filled else "40" if partial else "0",
            filled_avg_price="201.25" if filled or partial else None,
        )
    ).get_order_snapshot("order-123")

    assert snapshot.status is expected


def test_rejected_order_receives_broker_reason() -> None:
    snapshot = make_adapter(
        alpaca_order(
            status=OrderStatus.REJECTED,
            filled_qty="0",
            filled_avg_price=None,
            reject_reason="insufficient buying power",
        )
    ).get_order_snapshot("order-123")

    assert snapshot.rejection_reason == "insufficient buying power"


def test_fractional_order_quantity_fails_closed() -> None:
    with pytest.raises(ValueError, match="whole-share"):
        make_adapter(alpaca_order(qty="1.5")).get_order_snapshot("order-123")


def test_individual_fill_activities_are_translated_and_sorted() -> None:
    source = FillActivitySource(
        (
            SimpleNamespace(
                id="fill-2",
                order_id="order-123",
                symbol="NVDA",
                side="buy",
                qty="25",
                price="201.50",
                transaction_time=NOW + timedelta(seconds=2),
            ),
            SimpleNamespace(
                id="fill-1",
                order_id="order-123",
                symbol="NVDA",
                side="buy",
                qty="15",
                price="201.00",
                transaction_time=NOW + timedelta(seconds=1),
            ),
        )
    )

    fills = make_adapter(alpaca_order(), source).get_order_fills("order-123")

    assert tuple(fill.fill_id for fill in fills) == ("fill-1", "fill-2")
    assert tuple(fill.quantity for fill in fills) == (15, 25)
    assert source.requested_order_ids == ["order-123"]


def test_fill_retrieval_without_activity_source_fails_clearly() -> None:
    with pytest.raises(RuntimeError, match="fill activity source"):
        make_adapter(alpaca_order()).get_order_fills("order-123")


def test_fill_for_different_order_is_rejected() -> None:
    source = FillActivitySource(
        (
            SimpleNamespace(
                id="fill-1",
                order_id="other-order",
                symbol="NVDA",
                side="buy",
                qty="40",
                price="201.25",
                transaction_time=NOW,
            ),
        )
    )

    with pytest.raises(ValueError, match="does not match"):
        make_adapter(alpaca_order(), source).get_order_fills("order-123")

