from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import (
    BrokerFill,
    BrokerOrderSnapshot,
)


@runtime_checkable
class BrokerOrderQueryPort(Protocol):
    """Broker-neutral boundary for retrieving broker order truth."""

    def get_order_snapshot(
        self,
        broker_order_id: str,
    ) -> BrokerOrderSnapshot:
        ...

    def get_order_fills(
        self,
        broker_order_id: str,
    ) -> tuple[BrokerFill, ...]:
        ...

