from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import BrokerDailyPnlSnapshot


@runtime_checkable
class BrokerDailyPnlPort(Protocol):
    """Read-only boundary for verified current-day broker P&L truth."""

    def get_daily_pnl(self) -> BrokerDailyPnlSnapshot:
        ...
