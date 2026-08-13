from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from imie.models import PositionProtectionReconciliationRecord


@runtime_checkable
class PositionProtectionReconciliationStore(Protocol):
    def save(self, record: PositionProtectionReconciliationRecord) -> None:
        ...

    def list_for_position(
        self,
        *,
        broker: str,
        symbol: str,
        position_updated_at: datetime,
        position_fill_ids: tuple[str, ...],
    ) -> tuple[PositionProtectionReconciliationRecord, ...]:
        ...

    def get_latest_for_position(
        self,
        *,
        broker: str,
        symbol: str,
        position_updated_at: datetime,
        position_fill_ids: tuple[str, ...],
    ) -> PositionProtectionReconciliationRecord | None:
        ...
