from datetime import datetime, timezone

from imie.execution import BrokerOrderQueryPort
from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
    BrokerOrderStatus,
)


NOW = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


class FakeBrokerOrderQueryAdapter:
    def get_order_snapshot(
        self,
        broker_order_id: str,
    ) -> BrokerOrderSnapshot:
        return BrokerOrderSnapshot(
            broker="fake",
            broker_order_id=broker_order_id,
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

    def get_order_fills(
        self,
        broker_order_id: str,
    ) -> tuple[BrokerFill, ...]:
        return (
            BrokerFill(
                broker="fake",
                broker_order_id=broker_order_id,
                fill_id="fill-1",
                symbol="NVDA",
                side="buy",
                quantity=40,
                price=201.25,
                executed_at=NOW,
            ),
        )


class IncompleteBrokerOrderQueryAdapter:
    def get_order_snapshot(
        self,
        broker_order_id: str,
    ) -> BrokerOrderSnapshot:
        raise NotImplementedError


def test_adapter_satisfies_broker_order_query_port() -> None:
    adapter: BrokerOrderQueryPort = FakeBrokerOrderQueryAdapter()

    assert isinstance(adapter, BrokerOrderQueryPort)

    snapshot = adapter.get_order_snapshot("order-123")
    fills = adapter.get_order_fills("order-123")

    assert snapshot.broker_order_id == "order-123"
    assert snapshot.status is BrokerOrderStatus.PARTIALLY_FILLED
    assert fills[0].broker_order_id == "order-123"
    assert fills[0].quantity == 40


def test_incomplete_adapter_does_not_satisfy_query_port() -> None:
    assert not isinstance(
        IncompleteBrokerOrderQueryAdapter(),
        BrokerOrderQueryPort,
    )

