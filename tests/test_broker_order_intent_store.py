from datetime import datetime, timezone

from imie.execution import BrokerOrderIntentStore
from imie.models import BrokerOrderIntentRecord, ExecutionOrderIntent


class MemoryIntentStore:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], BrokerOrderIntentRecord] = {}

    def save(self, record: BrokerOrderIntentRecord) -> None:
        self.records[record.key] = record

    def get(
        self,
        *,
        broker: str,
        broker_order_id: str,
    ) -> BrokerOrderIntentRecord | None:
        return self.records.get((broker, broker_order_id))


class IncompleteIntentStore:
    def save(self, record: BrokerOrderIntentRecord) -> None:
        pass


def make_record() -> BrokerOrderIntentRecord:
    return BrokerOrderIntentRecord(
        broker="alpaca-paper",
        broker_order_id="order-123",
        intent=ExecutionOrderIntent(
            symbol="NVDA",
            side="buy",
            quantity=40,
            order_type="limit",
            entry_price=201.0,
            stop_price=200.0,
            target1_price=202.0,
            target2_price=203.0,
            time_in_force="day",
            valid=True,
            actionable=True,
        ),
        recorded_at=datetime(2026, 8, 13, 19, 0, tzinfo=timezone.utc),
        submission_label="target1",
    )


def test_store_contract_saves_and_retrieves_by_broker_order_key() -> None:
    store: BrokerOrderIntentStore = MemoryIntentStore()
    record = make_record()

    assert isinstance(store, BrokerOrderIntentStore)
    store.save(record)

    assert store.get(
        broker="alpaca-paper",
        broker_order_id="order-123",
    ) is record
    assert store.get(
        broker="alpaca-paper",
        broker_order_id="missing",
    ) is None


def test_incomplete_store_does_not_satisfy_contract() -> None:
    assert not isinstance(IncompleteIntentStore(), BrokerOrderIntentStore)

