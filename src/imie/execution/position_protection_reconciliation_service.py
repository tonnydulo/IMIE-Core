from __future__ import annotations

from imie.execution.broker_order_query_port import BrokerOrderQueryPort
from imie.execution.position_protection_reconciliation_engine import (
    PositionProtectionReconciliationEngine,
)
from imie.execution.position_protection_store import PositionProtectionStore
from imie.execution.position_protection_reconciliation_store import (
    PositionProtectionReconciliationStore,
)
from imie.execution.position_state_store import PositionStateStore
from datetime import datetime, timezone
from typing import Callable
from imie.models import (
    BrokerOrderSnapshot,
    ExecutionPosition,
    PositionProtectionRecord,
    PositionProtectionReconciliationResult,
    PositionProtectionReconciliationRecord,
)


class PositionProtectionReconciliationService:
    """Query broker truth once for current accepted position protection."""

    def __init__(
        self,
        *,
        position_store: PositionStateStore,
        protection_store: PositionProtectionStore,
        query_port: BrokerOrderQueryPort,
        reconciliation_store: PositionProtectionReconciliationStore | None = None,
        engine: PositionProtectionReconciliationEngine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(position_store, PositionStateStore):
            raise TypeError("position_store must satisfy PositionStateStore.")
        if not isinstance(protection_store, PositionProtectionStore):
            raise TypeError("protection_store must satisfy PositionProtectionStore.")
        if not isinstance(query_port, BrokerOrderQueryPort):
            raise TypeError("query_port must satisfy BrokerOrderQueryPort.")
        if reconciliation_store is not None and not isinstance(
            reconciliation_store, PositionProtectionReconciliationStore
        ):
            raise TypeError(
                "reconciliation_store must satisfy "
                "PositionProtectionReconciliationStore or be None."
            )
        resolved_engine = engine or PositionProtectionReconciliationEngine()
        if not isinstance(
            resolved_engine, PositionProtectionReconciliationEngine
        ):
            raise TypeError(
                "engine must be a PositionProtectionReconciliationEngine or None."
            )
        self._position_store = position_store
        self._protection_store = protection_store
        self._query_port = query_port
        self._reconciliation_store = reconciliation_store
        self._engine = resolved_engine
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._clock = resolved_clock

    def reconcile(
        self, *, broker: str, symbol: str
    ) -> PositionProtectionReconciliationResult:
        position = self._position_store.get(broker=broker, symbol=symbol)
        if position is None:
            raise LookupError("No reconciled position exists for protection query.")
        if not isinstance(position, ExecutionPosition):
            raise TypeError(
                "position_store.get() must return ExecutionPosition or None."
            )
        if position.is_flat:
            raise ValueError("A flat position has no active protection to reconcile.")
        record = self._protection_store.get_for_position(
            broker=position.broker,
            symbol=position.symbol,
            position_updated_at=position.last_updated_at,
            position_fill_ids=position.processed_fill_ids,
        )
        if record is None:
            raise LookupError(
                "No accepted protection record exists for the current position "
                "fingerprint."
            )
        if not isinstance(record, PositionProtectionRecord):
            raise TypeError(
                "protection_store.get_for_position() must return "
                "PositionProtectionRecord or None."
            )
        expected_ids = tuple(
            order_id
            for submission in record.result.submissions
            for order_id in (submission.target_order_id, submission.stop_order_id)
            if order_id is not None
        )
        if not expected_ids:
            raise ValueError("Accepted protection contains no broker order IDs.")
        if len(set(expected_ids)) != len(expected_ids):
            raise ValueError("Accepted protection contains duplicate broker order IDs.")

        snapshots: list[BrokerOrderSnapshot] = []
        for order_id in expected_ids:
            snapshot = self._query_port.get_order_snapshot(order_id)
            if not isinstance(snapshot, BrokerOrderSnapshot):
                raise TypeError(
                    "query_port.get_order_snapshot() must return "
                    "BrokerOrderSnapshot."
                )
            if snapshot.broker_order_id != order_id:
                raise ValueError(
                    "Broker snapshot order ID does not match the requested order ID."
                )
            snapshots.append(snapshot)
        result = self._engine.reconcile(
            protection=record.result,
            snapshots=tuple(snapshots),
        )
        if self._reconciliation_store is not None:
            observed_at = self._clock()
            if not isinstance(observed_at, datetime):
                raise TypeError("clock must return a datetime.")
            if observed_at.tzinfo is None:
                raise ValueError("clock must return a timezone-aware datetime.")
            self._reconciliation_store.save(
                PositionProtectionReconciliationRecord(
                    result=result,
                    position_updated_at=position.last_updated_at,
                    position_fill_ids=position.processed_fill_ids,
                    observed_at=observed_at,
                )
            )
        return result
