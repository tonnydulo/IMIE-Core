from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from imie.execution import (
    ExistingPositionProtectionGuard,
    ExistingPositionProtectionPlanBuilder,
)
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def position(**overrides):
    values = {
        "broker": "alpaca-paper",
        "symbol": "NVDA",
        "direction": PositionDirection.LONG,
        "quantity": 40,
        "average_entry_price": 200.0,
        "market_price": None,
        "unrealized_pnl": 0.0,
        "realized_pnl": 0.0,
        "last_updated_at": NOW,
        "processed_fill_ids": ("fill-1",),
    }
    values.update(overrides)
    return ExecutionPosition(**values)


def plan(current=None):
    current = current or position()
    intent = ExecutionOrderIntent(
        symbol="NVDA",
        side=("buy" if current.direction is PositionDirection.LONG else "sell"),
        quantity=40,
        order_type="limit",
        entry_price=200.0,
        stop_price=(199.0 if current.direction is PositionDirection.LONG else 201.0),
        target1_price=(201.0 if current.direction is PositionDirection.LONG else 199.0),
        target2_price=(202.0 if current.direction is PositionDirection.LONG else 198.0),
        time_in_force="gtc",
        valid=True,
        actionable=True,
    )
    coverage = ProtectiveCoverageAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        status=ProtectiveCoverageStatus.READY,
        position_quantity=40,
        protected_quantity=0,
        uncovered_quantity=40,
        actionable=True,
        reasons=("Protection required.",),
    )
    return ExistingPositionProtectionPlanBuilder().build(
        intent=intent, position=current, coverage=coverage
    )


def test_matching_fresh_position_passes_guard():
    current = position()

    assert ExistingPositionProtectionGuard().validate(
        plan=plan(current), current_position=current
    ) is None


def test_matching_short_position_passes_guard():
    current = position(
        direction=PositionDirection.SHORT,
        average_entry_price=200.0,
    )

    ExistingPositionProtectionGuard().validate(
        plan=plan(current), current_position=current
    )


@pytest.mark.parametrize(
    ("current", "message"),
    [
        (position(broker="other"), "broker"),
        (position(symbol="AMD"), "symbol"),
        (
            position(
                direction=PositionDirection.FLAT,
                quantity=0,
                average_entry_price=None,
            ),
            "flat",
        ),
        (
            position(
                direction=PositionDirection.SHORT,
                average_entry_price=200.0,
            ),
            "direction",
        ),
        (position(quantity=39), "quantity"),
        (position(last_updated_at=NOW + timedelta(seconds=1)), "timestamp"),
        (
            position(processed_fill_ids=("fill-1", "fill-2")),
            "fill checkpoint",
        ),
    ],
)
def test_changed_position_truth_blocks_stale_plan(current, message):
    with pytest.raises(ValueError, match=message):
        ExistingPositionProtectionGuard().validate(
            plan=plan(), current_position=current
        )


def test_exit_side_that_adds_exposure_is_rejected():
    current = position()
    unsafe_plan = replace(plan(current), exit_side="buy", position_side="sell")

    with pytest.raises(ValueError, match="direction|exit side"):
        ExistingPositionProtectionGuard().validate(
            plan=unsafe_plan, current_position=current
        )


def test_price_geometry_is_rechecked_against_current_average_entry():
    current = position(average_entry_price=198.0)

    with pytest.raises(ValueError, match="stop and targets"):
        ExistingPositionProtectionGuard().validate(
            plan=plan(), current_position=current
        )
