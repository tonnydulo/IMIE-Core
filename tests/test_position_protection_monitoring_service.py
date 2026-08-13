from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    PositionProtectionMonitoringEngine,
    PositionProtectionMonitoringService,
    PositionProtectionReconciliationHistoryService,
)
from imie.models import (
    ExecutionPosition,
    PositionDirection,
    PositionProtectionReconciliationRecord,
    PositionProtectionReconciliationResult,
)


NOW = datetime(2026, 8, 14, 4, 0, tzinfo=timezone.utc)


class PositionStore:
    def save(self, value):
        self.value = value

    def get(self, **kwargs):
        return position()


class HistoryStore:
    def __init__(self, value):
        self.value = value

    def save(self, value):
        self.value = value

    def list_for_position(self, **kwargs):
        return (self.value,) if self.value is not None else ()

    def get_latest_for_position(self, **kwargs):
        return self.value


def position():
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=2,
        average_entry_price=200.0,
        market_price=201.0,
        unrealized_pnl=2.0,
        realized_pnl=0.0,
        last_updated_at=NOW - timedelta(minutes=1),
        processed_fill_ids=("fill-1",),
    )


def record(age=5):
    return PositionProtectionReconciliationRecord(
        result=PositionProtectionReconciliationResult(
            broker="alpaca-paper",
            symbol="NVDA",
            state="active",
            requested_quantity=2,
            active_quantity=2,
            triggered_quantity=0,
            reconciled=True,
            snapshots=(),
        ),
        position_updated_at=position().last_updated_at,
        position_fill_ids=("fill-1",),
        observed_at=NOW - timedelta(seconds=age),
    )


def service(value, *, maximum_age=30, clock=lambda: NOW):
    history = PositionProtectionReconciliationHistoryService(
        position_store=PositionStore(),
        reconciliation_store=HistoryStore(value),
    )
    return PositionProtectionMonitoringService(
        history_service=history,
        engine=PositionProtectionMonitoringEngine(
            maximum_age_seconds=maximum_age
        ),
        clock=clock,
    )


def test_assesses_latest_current_fingerprint_observation():
    assessment = service(record()).assess(
        broker="alpaca-paper", symbol="NVDA"
    )

    assert assessment.state == "fresh_healthy"
    assert assessment.observation_age_seconds == 5.0


def test_missing_current_observation_is_never_observed():
    assessment = service(None).assess(
        broker="alpaca-paper", symbol="NVDA"
    )

    assert assessment.state == "never_observed"
    assert assessment.action_required is True


def test_service_applies_explicit_maximum_age():
    assessment = service(record(age=6), maximum_age=5).assess(
        broker="alpaca-paper", symbol="NVDA"
    )

    assert assessment.state == "stale"


def test_naive_clock_fails_closed():
    with pytest.raises(ValueError, match="timezone-aware"):
        service(record(), clock=lambda: datetime(2026, 8, 14)).assess(
            broker="alpaca-paper", symbol="NVDA"
        )
