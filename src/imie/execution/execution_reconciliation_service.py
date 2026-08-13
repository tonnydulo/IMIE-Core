from __future__ import annotations

from imie.execution.broker_order_query_port import BrokerOrderQueryPort
from imie.execution.execution_reconciliation_engine import (
    ExecutionReconciliationEngine,
)
from imie.models import (
    BrokerOrderSnapshot,
    ExecutionOrderIntent,
    ExecutionReconciliationResult,
)


class ExecutionReconciliationService:
    """Explicitly perform one broker query and reconciliation pass."""

    def __init__(
        self,
        *,
        query_port: BrokerOrderQueryPort,
        engine: ExecutionReconciliationEngine | None = None,
    ) -> None:
        if not isinstance(query_port, BrokerOrderQueryPort):
            raise TypeError(
                "query_port must satisfy BrokerOrderQueryPort."
            )
        resolved_engine = engine or ExecutionReconciliationEngine()
        if not isinstance(resolved_engine, ExecutionReconciliationEngine):
            raise TypeError(
                "engine must be an ExecutionReconciliationEngine or None."
            )
        self._query_port = query_port
        self._engine = resolved_engine

    def reconcile_order(
        self,
        *,
        intent: ExecutionOrderIntent,
        broker_order_id: str,
    ) -> ExecutionReconciliationResult:
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        order_id = self._normalize_order_id(broker_order_id)

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

        fills = self._query_port.get_order_fills(order_id)
        return self._engine.reconcile(
            intent=intent,
            snapshot=snapshot,
            fills=fills,
        )

    @staticmethod
    def _normalize_order_id(value: object) -> str:
        if not isinstance(value, str):
            raise TypeError("broker_order_id must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError("broker_order_id cannot be empty.")
        return normalized

