from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from imie.models import PositionProtectionAttempt


@runtime_checkable
class PositionProtectionAttemptStore(Protocol):
    def reserve(self, attempt: PositionProtectionAttempt) -> None:
        ...

    def get_for_position(
        self, *, broker: str, symbol: str, position_updated_at: datetime,
        position_fill_ids: tuple[str, ...]
    ) -> PositionProtectionAttempt | None:
        ...

    def transition(self, attempt: PositionProtectionAttempt) -> None:
        ...
