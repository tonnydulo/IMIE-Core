from datetime import datetime, timezone

import pytest

from imie.execution import ExistingPositionProtectionPlanBuilder
from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    PositionDirection,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


def intent(*, side="buy", stop=199.0, target1=201.0, target2=202.0):
    return ExecutionOrderIntent(
        symbol="NVDA",
        side=side,
        quantity=100,
        order_type="limit",
        entry_price=200.0,
        stop_price=stop,
        target1_price=target1,
        target2_price=target2,
        time_in_force="gtc",
        valid=True,
        actionable=True,
    )


def position(
    *,
    direction=PositionDirection.LONG,
    quantity=40,
    processed_fill_ids=("fill-1",),
):
    return ExecutionPosition(
        broker="alpaca-paper",
        symbol="NVDA",
        direction=direction,
        quantity=quantity,
        average_entry_price=200.0,
        market_price=None,
        unrealized_pnl=0.0,
        realized_pnl=0.0,
        last_updated_at=NOW,
        processed_fill_ids=processed_fill_ids,
    )


def coverage(*, protected=0, uncovered=40, status=ProtectiveCoverageStatus.READY):
    return ProtectiveCoverageAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        status=status,
        position_quantity=protected + uncovered,
        protected_quantity=protected,
        uncovered_quantity=uncovered,
        actionable=True,
        reasons=("Protection required.",),
    )


def test_long_position_plan_uses_sell_exit_without_new_entry():
    plan = ExistingPositionProtectionPlanBuilder().build(
        intent=intent(), position=position(), coverage=coverage()
    )

    assert isinstance(plan, ExistingPositionProtectionPlan)
    assert plan.position_side == "buy"
    assert plan.exit_side == "sell"
    assert plan.uncovered_quantity == 40
    assert tuple(item.quantity for item in plan.slices) == (20, 20)
    assert plan.stop_price == 199.0
    assert plan.position_updated_at == NOW
    assert plan.position_fill_ids == ("fill-1",)


def test_short_position_plan_uses_buy_exit():
    plan = ExistingPositionProtectionPlanBuilder().build(
        intent=intent(side="sell", stop=201.0, target1=199.0, target2=198.0),
        position=position(direction=PositionDirection.SHORT),
        coverage=coverage(),
    )

    assert plan.position_side == "sell"
    assert plan.exit_side == "buy"
    assert tuple(item.target_price for item in plan.slices) == (199.0, 198.0)


def test_partial_coverage_plans_only_uncovered_quantity():
    plan = ExistingPositionProtectionPlanBuilder().build(
        intent=intent(),
        position=position(),
        coverage=coverage(
            protected=25,
            uncovered=15,
            status=ProtectiveCoverageStatus.PARTIALLY_PROTECTED,
        ),
    )

    assert plan.protected_quantity == 25
    assert plan.uncovered_quantity == 15
    assert tuple(item.quantity for item in plan.slices) == (8, 7)


def test_one_uncovered_share_uses_target1_only():
    plan = ExistingPositionProtectionPlanBuilder().build(
        intent=intent(),
        position=position(),
        coverage=coverage(
            protected=39,
            uncovered=1,
            status=ProtectiveCoverageStatus.PARTIALLY_PROTECTED,
        ),
    )

    assert len(plan.slices) == 1
    assert plan.slices[0].label == "target1"
    assert "Target 1 only" in plan.warnings[0]


@pytest.mark.parametrize(
    ("intent_value", "position_value", "message"),
    [
        (intent(stop=201.0), position(), "do not protect"),
        (intent(target1=199.0), position(), "do not protect"),
        (
            intent(side="sell", stop=199.0, target1=201.0, target2=202.0),
            position(),
            "intent side",
        ),
        (
            intent(side="sell", stop=199.0, target1=201.0, target2=202.0),
            position(direction=PositionDirection.SHORT),
            "do not protect",
        ),
    ],
)
def test_invalid_directional_protection_is_rejected(
    intent_value, position_value, message
):
    with pytest.raises(ValueError, match=message):
        ExistingPositionProtectionPlanBuilder().build(
            intent=intent_value,
            position=position_value,
            coverage=coverage(),
        )


def test_non_actionable_coverage_cannot_build_plan():
    value = ProtectiveCoverageAssessment(
        broker="alpaca-paper",
        symbol="NVDA",
        status=ProtectiveCoverageStatus.PROTECTED,
        position_quantity=40,
        protected_quantity=40,
        uncovered_quantity=0,
        actionable=False,
        reasons=("Already protected.",),
    )

    with pytest.raises(ValueError, match="actionable"):
        ExistingPositionProtectionPlanBuilder().build(
            intent=intent(), position=position(), coverage=value
        )


def test_coverage_quantity_must_match_position():
    with pytest.raises(ValueError, match="coverage quantity"):
        ExistingPositionProtectionPlanBuilder().build(
            intent=intent(),
            position=position(quantity=41),
            coverage=coverage(),
        )
