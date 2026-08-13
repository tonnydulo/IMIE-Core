from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from imie.execution.position_protection_monitoring_engine import (
    PositionProtectionMonitoringEngine,
)
from imie.execution.position_protection_reconciliation_history_service import (
    PositionProtectionReconciliationHistoryService,
)
from imie.models import PositionProtectionMonitoringAssessment


class PositionProtectionMonitoringService:
    """Assess the latest local observation for the current position checkpoint."""

    def __init__(
        self,
        *,
        history_service: PositionProtectionReconciliationHistoryService,
        engine: PositionProtectionMonitoringEngine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(
            history_service, PositionProtectionReconciliationHistoryService
        ):
            raise TypeError(
                "history_service must be a "
                "PositionProtectionReconciliationHistoryService."
            )
        resolved_engine = engine or PositionProtectionMonitoringEngine()
        if not isinstance(resolved_engine, PositionProtectionMonitoringEngine):
            raise TypeError(
                "engine must be a PositionProtectionMonitoringEngine or None."
            )
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._history_service = history_service
        self._engine = resolved_engine
        self._clock = resolved_clock

    def assess(
        self, *, broker: str, symbol: str
    ) -> PositionProtectionMonitoringAssessment:
        record = self._history_service.get_latest_current(
            broker=broker,
            symbol=symbol,
        )
        checked_at = self._clock()
        if not isinstance(checked_at, datetime):
            raise TypeError("clock must return a datetime.")
        if checked_at.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        return self._engine.assess(
            broker=broker,
            symbol=symbol,
            record=record,
            checked_at=checked_at,
        )
