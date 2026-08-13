from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import ExecutionPosition


@runtime_checkable
class PositionStateStore(Protocol):
    """Persistence boundary for the latest broker-neutral position state."""

    def save(self, position: ExecutionPosition) -> None:
        ...

    def get(self, *, broker: str, symbol: str) -> ExecutionPosition | None:
        ...
