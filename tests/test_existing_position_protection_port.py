from datetime import datetime, timezone

import pytest

from imie.execution import ExistingPositionProtectionPort
from imie.models import (
    ExistingPositionProtectionResult,
    ExistingPositionProtectionSubmission,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def item(
    *,
    label="target1",
    quantity=20,
    accepted=True,
    target_order_id="target-1",
    stop_order_id="stop-1",
):
    return ExistingPositionProtectionSubmission(
        label=label,
        quantity=quantity,
        accepted=accepted,
        target_order_id=target_order_id,
        stop_order_id=stop_order_id,
        status="accepted" if accepted else "rejected",
        message="Paper protection result.",
    )


class StructuralAdapter:
    def submit_existing_position_protection(self, *, plan, current_position):
        raise NotImplementedError


def result(**overrides):
    submissions = overrides.pop(
        "submissions",
        (
            item(),
            item(
                label="target2",
                target_order_id="target-2",
                stop_order_id="stop-2",
            ),
        ),
    )
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "exit_side": "sell",
        "position_quantity": 40,
        "requested_quantity": 40,
        "accepted_quantity": 40,
        "position_updated_at": NOW,
        "accepted": True,
        "status": "accepted",
        "message": "Existing position protection accepted.",
        "submissions": submissions,
    }
    values.update(overrides)
    return ExistingPositionProtectionResult(**values)


def test_structural_adapter_satisfies_runtime_protocol():
    assert isinstance(StructuralAdapter(), ExistingPositionProtectionPort)


def test_accepted_result_represents_distinct_oco_exit_order_ids():
    value = result()

    assert value.accepted is True
    assert value.accepted_quantity == 40
    assert value.submissions[0].target_order_id == "target-1"
    assert value.submissions[0].stop_order_id == "stop-1"
    assert value.position_updated_at == NOW


def test_partial_result_is_not_fully_accepted():
    value = result(
        submissions=(
            item(),
            item(
                label="target2",
                accepted=False,
                target_order_id=None,
                stop_order_id=None,
            ),
        ),
        accepted_quantity=20,
        accepted=False,
        status="partial",
        rollback_attempted=True,
        rollback_succeeded=True,
    )

    assert value.accepted is False
    assert value.accepted_quantity == 20
    assert value.rollback_succeeded is True


def test_accepted_slice_requires_both_exit_order_ids():
    with pytest.raises(ValueError, match="target and stop order IDs"):
        item(stop_order_id=None)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"requested_quantity": 41}, "position quantity"),
        ({"accepted_quantity": 41}, "requested quantity"),
        ({"accepted_quantity": 20}, "does not match result"),
        ({"requested_quantity": 39}, "requested quantity"),
        (
            {
                "accepted": True,
                "submissions": (
                    item(),
                    item(
                        label="target2",
                        accepted=False,
                        target_order_id=None,
                        stop_order_id=None,
                    ),
                ),
                "accepted_quantity": 20,
            },
            "full requested coverage",
        ),
    ],
)
def test_inconsistent_result_quantities_are_rejected(overrides, message):
    with pytest.raises(ValueError, match=message):
        result(**overrides)


def test_position_timestamp_must_be_timezone_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        result(position_updated_at=datetime(2026, 8, 13, 20, 0))
