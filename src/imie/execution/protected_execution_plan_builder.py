from __future__ import annotations

from imie.models import (
    ExecutionOrderIntent,
    ProtectedExecutionPlan,
    ProtectedOrderSlice,
)


class ProtectedExecutionPlanBuilder:
    def build(
        self,
        intent: ExecutionOrderIntent,
    ) -> ProtectedExecutionPlan:
        if not isinstance(
            intent,
            ExecutionOrderIntent,
        ):
            raise TypeError(
                "intent must be an ExecutionOrderIntent."
            )

        if intent.quantity <= 0:
            raise ValueError(
                "intent quantity must be greater than zero."
            )

        target1_quantity = (
            intent.quantity + 1
        ) // 2
        target2_quantity = (
            intent.quantity
            - target1_quantity
        )

        slices = [
            ProtectedOrderSlice(
                label="target1",
                quantity=target1_quantity,
                stop_price=intent.stop_price,
                target_price=intent.target1_price,
            )
        ]

        warnings: tuple[str, ...] = ()

        if target2_quantity > 0:
            slices.append(
                ProtectedOrderSlice(
                    label="target2",
                    quantity=target2_quantity,
                    stop_price=intent.stop_price,
                    target_price=intent.target2_price,
                )
            )
        else:
            warnings = (
                "Quantity 1 cannot be split across two targets; "
                "the position uses Target 1 only.",
            )

        return ProtectedExecutionPlan(
            symbol=intent.symbol,
            side=intent.side,
            order_type=intent.order_type,
            entry_price=intent.entry_price,
            time_in_force=intent.time_in_force,
            slices=tuple(slices),
            valid=intent.valid,
            actionable=intent.actionable,
            warnings=warnings,
        )
