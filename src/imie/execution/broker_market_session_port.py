from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import BrokerMarketSessionSnapshot


@runtime_checkable
class BrokerMarketSessionPort(Protocol):
    """Read-only boundary for verified broker market-session truth."""

    def get_market_session(self) -> BrokerMarketSessionSnapshot:
        ...
