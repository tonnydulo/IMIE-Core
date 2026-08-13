from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import BrokerOrderIntentRecord


@runtime_checkable
class BrokerOrderIntentStore(Protocol):
    """Persistence boundary for exact submitted broker-order intents."""

    def save(self, record: BrokerOrderIntentRecord) -> None:
        ...

    def get(
        self,
        *,
        broker: str,
        broker_order_id: str,
    ) -> BrokerOrderIntentRecord | None:
        ...

