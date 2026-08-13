from datetime import datetime, timezone

import pytest

from imie.execution import PositionProtectionReconciliationEngine
from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
)


NOW = datetime(2026, 8, 13, 23, 0, tzinfo=timezone.utc)


def submission(label, quantity, number):
    return ExistingPositionProtectionSubmission(
        label=label,
        quantity=quantity,
        accepted=True,
        target_order_id=f"target-{number}",
        stop_order_id=f"stop-{number}",
        status="accepted",
        message="Paper OCO accepted.",
    )


def protection():
    return ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=5,
        requested_quantity=5,
        accepted_quantity=5,
        position_updated_at=NOW,
        accepted=True,
        status="accepted",
        message="Protection accepted.",
        submissions=(submission("target1", 3, 1), submission("target2", 2, 2)),
    )


def snapshot(order_id, quantity, status=BrokerOrderStatus.ACCEPTED, **overrides):
    filled = quantity if status is BrokerOrderStatus.FILLED else 0
    values = {
        "broker": "alpaca-paper",
        "broker_order_id": order_id,
        "symbol": "NVDA",
        "side": "sell",
        "order_type": "limit" if order_id.startswith("target") else "stop",
        "status": status,
        "requested_quantity": quantity,
        "filled_quantity": filled,
        "remaining_quantity": quantity - filled,
        "average_fill_price": 201.0 if filled else None,
        "last_updated_at": NOW,
    }
    values.update(overrides)
    return BrokerOrderSnapshot(**values)


def all_snapshots(status=BrokerOrderStatus.ACCEPTED):
    return (
        snapshot("target-1", 3, status),
        snapshot("stop-1", 3, status),
        snapshot("target-2", 2, status),
        snapshot("stop-2", 2, status),
    )


def test_all_protective_legs_active_reconcile():
    result = PositionProtectionReconciliationEngine().reconcile(
        protection=protection(), snapshots=all_snapshots()
    )

    assert result.state == "active"
    assert result.active_quantity == 5
    assert result.triggered_quantity == 0
    assert result.reconciled is True


def test_filled_protective_leg_reports_triggered_quantity():
    snapshots = list(all_snapshots())
    snapshots[0] = snapshot("target-1", 3, BrokerOrderStatus.FILLED)

    result = PositionProtectionReconciliationEngine().reconcile(
        protection=protection(), snapshots=tuple(snapshots)
    )

    assert result.state == "triggered"
    assert result.triggered_quantity == 3
    assert result.active_quantity == 2
    assert result.reconciled is True


def test_one_terminal_leg_with_active_sibling_is_degraded():
    snapshots = list(all_snapshots())
    snapshots[0] = snapshot("target-1", 3, BrokerOrderStatus.CANCELED)

    result = PositionProtectionReconciliationEngine().reconcile(
        protection=protection(), snapshots=tuple(snapshots)
    )

    assert result.state == "degraded"
    assert result.active_quantity == 2


def test_all_terminal_legs_report_terminal_unprotected():
    result = PositionProtectionReconciliationEngine().reconcile(
        protection=protection(),
        snapshots=all_snapshots(BrokerOrderStatus.CANCELED),
    )

    assert result.state == "terminal_unprotected"
    assert result.active_quantity == 0
    assert result.reconciled is True


@pytest.mark.parametrize(
    "snapshots, discrepancy",
    [
        (lambda: all_snapshots()[:-1], "missing broker snapshots"),
        (
            lambda: all_snapshots()
            + (snapshot("unexpected", 1),),
            "Unexpected broker snapshots",
        ),
        (
            lambda: (
                snapshot("target-1", 3, symbol="AAPL"),
                *all_snapshots()[1:],
            ),
            "symbol does not match",
        ),
        (
            lambda: all_snapshots() + (snapshot("target-1", 3),),
            "Duplicate snapshot",
        ),
    ],
)
def test_discrepant_broker_truth_is_indeterminate(snapshots, discrepancy):
    result = PositionProtectionReconciliationEngine().reconcile(
        protection=protection(), snapshots=snapshots()
    )

    assert result.state == "indeterminate"
    assert result.reconciled is False
    assert any(discrepancy in item for item in result.discrepancies)


def test_rejects_nonaccepted_local_protection_result():
    rejected = ExistingPositionProtectionResult(
        broker="alpaca-paper",
        symbol="NVDA",
        exit_side="sell",
        position_quantity=3,
        requested_quantity=3,
        accepted_quantity=0,
        position_updated_at=NOW,
        accepted=False,
        status="rejected",
        message="Rejected.",
        submissions=(
            ExistingPositionProtectionSubmission(
                label="target1",
                quantity=3,
                accepted=False,
                target_order_id=None,
                stop_order_id=None,
                status="rejected",
                message="Rejected.",
            ),
        ),
    )

    with pytest.raises(ValueError, match="accepted result"):
        PositionProtectionReconciliationEngine().reconcile(
            protection=rejected, snapshots=()
        )
