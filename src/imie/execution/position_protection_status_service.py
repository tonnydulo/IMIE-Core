from __future__ import annotations

from imie.execution.position_protection_attempt_store import (
    PositionProtectionAttemptStore,
)
from imie.execution.position_protection_store import PositionProtectionStore
from imie.execution.position_state_store import PositionStateStore
from imie.models import PositionProtectionStatus


class PositionProtectionStatusService:
    """Read current protection state without broker access or mutation."""

    def __init__(
        self,
        *,
        position_store: PositionStateStore,
        protection_store: PositionProtectionStore,
        attempt_store: PositionProtectionAttemptStore,
    ) -> None:
        if not isinstance(position_store, PositionStateStore):
            raise TypeError("position_store must satisfy PositionStateStore.")
        if not isinstance(protection_store, PositionProtectionStore):
            raise TypeError("protection_store must satisfy PositionProtectionStore.")
        if not isinstance(attempt_store, PositionProtectionAttemptStore):
            raise TypeError(
                "attempt_store must satisfy PositionProtectionAttemptStore."
            )
        self._position_store = position_store
        self._protection_store = protection_store
        self._attempt_store = attempt_store

    def get(self, *, broker: str, symbol: str) -> PositionProtectionStatus:
        position = self._position_store.get(broker=broker, symbol=symbol)
        if position is None:
            return PositionProtectionStatus(
                broker=broker,
                symbol=symbol,
                state="no_position",
                position=None,
                attempt=None,
                record=None,
            )
        if position.is_flat:
            return PositionProtectionStatus(
                broker=position.broker,
                symbol=position.symbol,
                state="flat",
                position=position,
                attempt=None,
                record=None,
            )
        key = {
            "broker": position.broker,
            "symbol": position.symbol,
            "position_updated_at": position.last_updated_at,
            "position_fill_ids": position.processed_fill_ids,
        }
        record = self._protection_store.get_for_position(**key)
        attempt = self._attempt_store.get_for_position(**key)
        state = "unprotected"
        if record is not None:
            state = "accepted"
        elif attempt is not None:
            state = attempt.status.value
        return PositionProtectionStatus(
            broker=position.broker,
            symbol=position.symbol,
            state=state,
            position=position,
            attempt=attempt,
            record=record,
        )
