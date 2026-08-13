from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from imie.models import PositionProtectionRecord


@runtime_checkable
class PositionProtectionStore(Protocol):
    def save(self, record: PositionProtectionRecord) -> None:
        ...

    def get_for_position(
        self,
        *,
        broker: str,
        symbol: str,
        position_updated_at: datetime,
        position_fill_ids: tuple[str, ...],
    ) -> PositionProtectionRecord | None:
        ...
