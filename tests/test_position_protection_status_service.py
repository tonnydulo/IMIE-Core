from datetime import datetime, timezone

from imie.execution import PositionProtectionStatusService
from imie.models import (
    ExecutionPosition,
    PositionDirection,
    PositionProtectionAttempt,
    PositionProtectionAttemptStatus,
)


NOW = datetime(2026, 8, 13, 22, 0, tzinfo=timezone.utc)


class PositionStore:
    def __init__(self, value):
        self.value = value

    def save(self, position):
        self.value = position

    def get(self, **kwargs):
        return self.value


class ProtectionStore:
    def __init__(self, value=None):
        self.value = value

    def save(self, record):
        self.value = record

    def get_for_position(self, **kwargs):
        return self.value


class AttemptStore:
    def __init__(self, value=None):
        self.value = value

    def reserve(self, attempt):
        self.value = attempt

    def transition(self, attempt):
        self.value = attempt

    def get_for_position(self, **kwargs):
        return self.value


def position():
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.LONG,
        quantity=5,
        average_entry_price=200.0,
        market_price=201.0,
        unrealized_pnl=5.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1",),
    )


def service(position_value, attempt=None, record=None):
    return PositionProtectionStatusService(
        position_store=PositionStore(position_value),
        protection_store=ProtectionStore(record),
        attempt_store=AttemptStore(attempt),
    )


def test_reports_no_position_without_querying_broker():
    status = service(None).get(broker="alpaca-paper", symbol="nvda")

    assert status.state == "no_position"
    assert status.position is None


def test_reports_current_position_as_unprotected_without_ledgers():
    status = service(position()).get(broker="alpaca-paper", symbol="NVDA")

    assert status.state == "unprotected"
    assert status.position.quantity == 5


def test_reports_flat_position_as_not_requiring_protection():
    flat = ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=PositionDirection.FLAT,
        quantity=0,
        average_entry_price=None,
        market_price=201.0,
        unrealized_pnl=0.0,
        realized_pnl=5.0,
        last_updated_at=NOW,
        processed_fill_ids=("fill-1", "fill-2"),
    )

    status = service(flat).get(broker="alpaca-paper", symbol="NVDA")

    assert status.state == "flat"
    assert status.attempt is None


def test_reports_uncertain_attempt_for_current_fingerprint():
    attempt = PositionProtectionAttempt(
        attempt_id="attempt-1",
        broker="alpaca-paper",
        symbol="NVDA",
        position_updated_at=NOW,
        position_fill_ids=("fill-1",),
        status=PositionProtectionAttemptStatus.UNCERTAIN,
        created_at=NOW,
        updated_at=NOW,
        message="Broker outcome requires review.",
    )

    status = service(position(), attempt=attempt).get(
        broker="alpaca-paper", symbol="NVDA"
    )

    assert status.state == "uncertain"
    assert status.attempt is attempt
