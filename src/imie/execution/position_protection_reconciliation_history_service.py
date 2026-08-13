from __future__ import annotations

from imie.execution.position_protection_reconciliation_store import (
    PositionProtectionReconciliationStore,
)
from imie.execution.position_state_store import PositionStateStore
from imie.models import (
    ExecutionPosition,
    PositionProtectionReconciliationRecord,
)


class PositionProtectionReconciliationHistoryService:
    """Read observations for the current position fingerprint only."""

    def __init__(
        self,
        *,
        position_store: PositionStateStore,
        reconciliation_store: PositionProtectionReconciliationStore,
    ) -> None:
        if not isinstance(position_store, PositionStateStore):
            raise TypeError("position_store must satisfy PositionStateStore.")
        if not isinstance(
            reconciliation_store, PositionProtectionReconciliationStore
        ):
            raise TypeError(
                "reconciliation_store must satisfy "
                "PositionProtectionReconciliationStore."
            )
        self._position_store = position_store
        self._reconciliation_store = reconciliation_store

    def list_current(
        self, *, broker: str, symbol: str
    ) -> tuple[PositionProtectionReconciliationRecord, ...]:
        position = self._position_store.get(broker=broker, symbol=symbol)
        if position is None:
            raise LookupError("No reconciled position exists for history query.")
        if not isinstance(position, ExecutionPosition):
            raise TypeError(
                "position_store.get() must return ExecutionPosition or None."
            )
        records = self._reconciliation_store.list_for_position(
            broker=position.broker,
            symbol=position.symbol,
            position_updated_at=position.last_updated_at,
            position_fill_ids=position.processed_fill_ids,
        )
        if not isinstance(records, tuple) or not all(
            isinstance(item, PositionProtectionReconciliationRecord)
            for item in records
        ):
            raise TypeError(
                "reconciliation_store.list_for_position() must return a tuple "
                "of PositionProtectionReconciliationRecord."
            )
        return tuple(sorted(records, key=lambda item: item.observed_at))

    def get_latest_current(
        self, *, broker: str, symbol: str
    ) -> PositionProtectionReconciliationRecord | None:
        records = self.list_current(broker=broker, symbol=symbol)
        return records[-1] if records else None
