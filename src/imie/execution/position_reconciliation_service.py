from __future__ import annotations

from imie.execution.broker_order_query_port import BrokerOrderQueryPort
from imie.execution.position_state_engine import PositionStateEngine
from imie.execution.position_state_store import PositionStateStore
from imie.models import BrokerFill, ExecutionPosition, PositionDirection


class PositionReconciliationService:
    """Explicitly apply broker order fills to persisted position state."""

    def __init__(
        self,
        *,
        query_port: BrokerOrderQueryPort,
        position_store: PositionStateStore,
        engine: PositionStateEngine | None = None,
    ) -> None:
        if not isinstance(query_port, BrokerOrderQueryPort):
            raise TypeError("query_port must satisfy BrokerOrderQueryPort.")
        if not isinstance(position_store, PositionStateStore):
            raise TypeError("position_store must satisfy PositionStateStore.")
        resolved_engine = engine or PositionStateEngine()
        if not isinstance(resolved_engine, PositionStateEngine):
            raise TypeError("engine must be a PositionStateEngine or None.")
        self._query_port = query_port
        self._position_store = position_store
        self._engine = resolved_engine

    def reconcile_order_position(
        self,
        *,
        broker: str,
        broker_order_id: str,
        symbol: str,
        market_price: float | None = None,
    ) -> ExecutionPosition | None:
        normalized_broker = self._required_text(broker, "broker").lower()
        order_id = self._required_text(
            broker_order_id, "broker_order_id"
        )
        normalized_symbol = self._required_text(symbol, "symbol").upper()

        current = self._position_store.get(
            broker=normalized_broker,
            symbol=normalized_symbol,
        )
        if current is not None and not isinstance(current, ExecutionPosition):
            raise TypeError(
                "position_store.get() must return ExecutionPosition or None."
            )

        fills = self._query_port.get_order_fills(order_id)
        if not isinstance(fills, tuple) or not all(
            isinstance(fill, BrokerFill) for fill in fills
        ):
            raise TypeError(
                "query_port.get_order_fills() must return a tuple of BrokerFill."
            )
        for fill in fills:
            if fill.broker != normalized_broker:
                raise ValueError("Broker fill does not match requested broker.")
            if fill.broker_order_id != order_id:
                raise ValueError("Broker fill does not match requested order ID.")
            if fill.symbol != normalized_symbol:
                raise ValueError("Broker fill does not match requested symbol.")

        if current is None:
            if not fills:
                return None
            current = ExecutionPosition(
                broker=normalized_broker,
                symbol=normalized_symbol,
                direction=PositionDirection.FLAT,
                quantity=0,
                average_entry_price=None,
                market_price=None,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                last_updated_at=fills[0].executed_at,
            )

        if not any(
            fill.fill_id not in current.processed_fill_ids for fill in fills
        ):
            return current

        updated = self._engine.apply_fills(
            position=current,
            fills=fills,
            market_price=market_price,
        )
        if updated != current:
            self._position_store.save(updated)
        return updated

    @staticmethod
    def _required_text(value: object, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{name} cannot be empty.")
        return normalized
