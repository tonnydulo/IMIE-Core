from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import PositionProtectionReconciliationHistoryService
from imie.models import (
    ExecutionPosition,
    PositionDirection,
    PositionProtectionReconciliationRecord,
    PositionProtectionReconciliationResult,
)


NOW = datetime(2026, 8, 14, 2, 0, tzinfo=timezone.utc)


class PositionStore:
    def __init__(self, value):
        self.value = value

    def save(self, value):
        self.value = value

    def get(self, **kwargs):
        return self.value


class HistoryStore:
    def __init__(self, records=()):
        self.records = records
        self.calls = []

    def save(self, record):
        self.records += (record,)

    def list_for_position(self, **kwargs):
        self.calls.append(kwargs)
        return self.records

    def get_latest_for_position(self, **kwargs):
        values = self.list_for_position(**kwargs)
        return values[-1] if values else None


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
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def record(seconds):
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
        position_updated_at=NOW,
        position_fill_ids=("fill-1",),
        observed_at=NOW + timedelta(seconds=seconds),
    )


def test_lists_current_fingerprint_in_observation_order():
    history = HistoryStore((record(20), record(10)))
    service = PositionProtectionReconciliationHistoryService(
        position_store=PositionStore(position()),
        reconciliation_store=history,
    )

    records = service.list_current(broker="alpaca-paper", symbol="NVDA")

    assert [item.observed_at for item in records] == [
        NOW + timedelta(seconds=10),
        NOW + timedelta(seconds=20),
    ]
    assert history.calls == [{
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "position_updated_at": NOW,
        "position_fill_ids": ("fill-1",),
    }]


def test_latest_returns_none_when_current_fingerprint_has_no_history():
    service = PositionProtectionReconciliationHistoryService(
        position_store=PositionStore(position()),
        reconciliation_store=HistoryStore(),
    )

    assert service.get_latest_current(
        broker="alpaca-paper", symbol="NVDA"
    ) is None


def test_missing_position_fails_before_history_read():
    history = HistoryStore()
    service = PositionProtectionReconciliationHistoryService(
        position_store=PositionStore(None),
        reconciliation_store=history,
    )

    with pytest.raises(LookupError, match="No reconciled position"):
        service.list_current(broker="alpaca-paper", symbol="NVDA")

    assert history.calls == []
