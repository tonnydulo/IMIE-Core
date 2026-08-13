import pytest

from imie.execution import (
    ProtectedExecutionPlanBuilder,
)
from imie.models import (
    ExecutionOrderIntent,
    ProtectedExecutionPlan,
)


def make_intent(
    **overrides: object,
) -> ExecutionOrderIntent:
    values = {
        "symbol": "NVDA",
        "side": "buy",
        "quantity": 100,
        "order_type": "limit",
        "entry_price": 500.0,
        "stop_price": 499.0,
        "target1_price": 501.0,
        "target2_price": 502.0,
        "time_in_force": "day",
        "valid": True,
        "actionable": True,
    }
    values.update(overrides)
    return ExecutionOrderIntent(**values)


def test_even_quantity_is_split_equally() -> None:
    plan = ProtectedExecutionPlanBuilder().build(
        make_intent(quantity=100)
    )

    assert isinstance(plan, ProtectedExecutionPlan)
    assert plan.quantity == 100
    assert tuple(
        item.quantity
        for item in plan.slices
    ) == (50, 50)
    assert tuple(
        item.target_price
        for item in plan.slices
    ) == (501.0, 502.0)
    assert all(
        item.stop_price == 499.0
        for item in plan.slices
    )
    assert plan.warnings == ()


def test_odd_quantity_assigns_extra_share_to_target1() -> None:
    plan = ProtectedExecutionPlanBuilder().build(
        make_intent(quantity=125)
    )

    assert tuple(
        item.quantity
        for item in plan.slices
    ) == (63, 62)
    assert plan.quantity == 125


def test_single_share_uses_target1_with_warning() -> None:
    plan = ProtectedExecutionPlanBuilder().build(
        make_intent(quantity=1)
    )

    assert len(plan.slices) == 1
    assert plan.slices[0].label == "target1"
    assert plan.slices[0].quantity == 1
    assert plan.slices[0].target_price == 501.0
    assert plan.warnings == (
        "Quantity 1 cannot be split across two targets; "
        "the position uses Target 1 only.",
    )


def test_plan_preserves_entry_and_actionability() -> None:
    plan = ProtectedExecutionPlanBuilder().build(
        make_intent(
            side="sell",
            order_type="market",
            entry_price=None,
            time_in_force="gtc",
            actionable=False,
        )
    )

    assert plan.symbol == "NVDA"
    assert plan.side == "sell"
    assert plan.order_type == "market"
    assert plan.entry_price is None
    assert plan.time_in_force == "gtc"
    assert plan.valid is True
    assert plan.actionable is False


def test_zero_quantity_intent_cannot_build_plan() -> None:
    builder = ProtectedExecutionPlanBuilder()

    with pytest.raises(
        ValueError,
        match="quantity",
    ):
        builder.build(
            make_intent(
                quantity=0,
                actionable=False,
            )
        )


def test_invalid_intent_type_raises() -> None:
    with pytest.raises(
        TypeError,
        match="ExecutionOrderIntent",
    ):
        ProtectedExecutionPlanBuilder().build(
            object()  # type: ignore[arg-type]
        )
