from __future__ import annotations

from imie.models import (
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    PositionDirection,
)


class ExistingPositionProtectionGuard:
    """Fail closed when a protection plan no longer matches position truth."""

    def validate(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        current_position: ExecutionPosition,
    ) -> None:
        if not isinstance(plan, ExistingPositionProtectionPlan):
            raise TypeError("plan must be an ExistingPositionProtectionPlan.")
        if not isinstance(current_position, ExecutionPosition):
            raise TypeError("current_position must be an ExecutionPosition.")
        if current_position.broker != plan.broker:
            raise ValueError("Current position broker does not match plan.")
        if current_position.symbol != plan.symbol:
            raise ValueError("Current position symbol does not match plan.")
        if current_position.is_flat:
            raise ValueError("Current position is flat; protection is stale.")

        position_side = (
            "buy"
            if current_position.direction is PositionDirection.LONG
            else "sell"
        )
        expected_exit_side = "sell" if position_side == "buy" else "buy"
        if position_side != plan.position_side:
            raise ValueError("Current position direction does not match plan.")
        if plan.exit_side != expected_exit_side:
            raise ValueError("Plan exit side does not reduce current position.")
        if current_position.quantity != plan.position_quantity:
            raise ValueError("Current position quantity does not match plan.")
        if current_position.last_updated_at != plan.position_updated_at:
            raise ValueError("Current position timestamp does not match plan.")
        if current_position.processed_fill_ids != plan.position_fill_ids:
            raise ValueError("Current position fill checkpoint does not match plan.")
        if plan.uncovered_quantity <= 0:
            raise ValueError("Plan has no uncovered quantity to protect.")
        if sum(item.quantity for item in plan.slices) != plan.uncovered_quantity:
            raise ValueError("Plan slice quantity does not match uncovered quantity.")
        if plan.uncovered_quantity > current_position.quantity:
            raise ValueError("Plan protection exceeds current position quantity.")

        entry = current_position.average_entry_price
        if entry is None:
            raise ValueError("Current open position requires average entry price.")
        targets = tuple(item.target_price for item in plan.slices)
        if current_position.direction is PositionDirection.LONG:
            geometry_valid = plan.stop_price < entry and all(
                target > entry for target in targets
            )
        else:
            geometry_valid = plan.stop_price > entry and all(
                target < entry for target in targets
            )
        if not geometry_valid:
            raise ValueError(
                "Plan stop and targets do not protect current position."
            )
