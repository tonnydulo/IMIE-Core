from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import PositionProtectionMonitoringEngine
from imie.models import (
    PositionProtectionReconciliationRecord,
    PositionProtectionReconciliationResult,
)


NOW = datetime(2026, 8, 14, 3, 0, tzinfo=timezone.utc)


def record(*, state="active", reconciled=True, age=5):
    return PositionProtectionReconciliationRecord(
        result=PositionProtectionReconciliationResult(
            broker="alpaca-paper",
            symbol="NVDA",
            state=state,
            requested_quantity=4,
            active_quantity=4 if state == "active" else 0,
            triggered_quantity=4 if state == "triggered" else 0,
            reconciled=reconciled,
            snapshots=(),
            warnings=("broker warning",) if state != "active" else (),
        ),
        position_updated_at=NOW - timedelta(minutes=1),
        position_fill_ids=("fill-1",),
        observed_at=NOW - timedelta(seconds=age),
    )


def assess(value, *, maximum_age=30):
    return PositionProtectionMonitoringEngine(
        maximum_age_seconds=maximum_age
    ).assess(
        broker="alpaca-paper",
        symbol="NVDA",
        record=value,
        checked_at=NOW,
    )


def test_never_observed_requires_action():
    result = assess(None)

    assert result.state == "never_observed"
    assert result.healthy is False
    assert result.action_required is True
    assert result.observation_age_seconds is None


def test_fresh_active_reconciled_truth_is_healthy():
    result = assess(record(age=10))

    assert result.state == "fresh_healthy"
    assert result.healthy is True
    assert result.action_required is False
    assert result.observation_age_seconds == 10.0


@pytest.mark.parametrize(
    "state",
    ["triggered", "degraded", "terminal_unprotected", "indeterminate"],
)
def test_fresh_nonactive_truth_requires_review(state):
    result = assess(record(state=state, reconciled=state != "indeterminate"))

    assert result.state == "fresh_unhealthy"
    assert result.reconciliation_state == state
    assert result.action_required is True


def test_unreconciled_active_truth_is_not_healthy():
    result = assess(record(state="active", reconciled=False))

    assert result.state == "fresh_unhealthy"
    assert result.healthy is False


def test_observation_older_than_limit_is_stale_even_if_active():
    result = assess(record(age=31), maximum_age=30)

    assert result.state == "stale"
    assert result.reconciliation_state == "active"
    assert result.action_required is True


def test_exact_age_boundary_remains_fresh():
    assert assess(record(age=30), maximum_age=30).state == "fresh_healthy"


def test_future_observation_fails_unhealthy_with_clock_warning():
    result = assess(record(age=-1))

    assert result.state == "fresh_unhealthy"
    assert result.observation_age_seconds == 0.0
    assert "Clock alignment" in result.warnings[0]


@pytest.mark.parametrize("value", [0, -1, float("inf"), True])
def test_maximum_age_must_be_finite_positive(value):
    with pytest.raises((TypeError, ValueError)):
        PositionProtectionMonitoringEngine(maximum_age_seconds=value)


def test_record_identity_must_match_requested_identity():
    with pytest.raises(ValueError, match="symbol"):
        PositionProtectionMonitoringEngine().assess(
            broker="alpaca-paper",
            symbol="AAPL",
            record=record(),
            checked_at=NOW,
        )
