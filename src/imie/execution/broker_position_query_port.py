from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import BrokerPositionSnapshot


@runtime_checkable
class BrokerPositionQueryPort(Protocol):
    """Read-only boundary for fresh broker position truth."""

    def get_position(self, symbol: str) -> BrokerPositionSnapshot | None:
        ...
