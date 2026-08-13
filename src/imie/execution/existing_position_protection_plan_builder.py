from __future__ import annotations

from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    PositionDirection,
    ProtectedOrderSlice,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


class ExistingPositionProtectionPlanBuilder:
    """Plan exit protection for uncovered shares of an existing position."""

    def build(
        self,
        *,
        intent: ExecutionOrderIntent,
        position: ExecutionPosition,
        coverage: ProtectiveCoverageAssessment,
    ) -> ExistingPositionProtectionPlan:
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        if not isinstance(position, ExecutionPosition):
            raise TypeError("position must be an ExecutionPosition.")
        if not isinstance(coverage, ProtectiveCoverageAssessment):
            raise TypeError("coverage must be a ProtectiveCoverageAssessment.")
        if coverage.status not in {
            ProtectiveCoverageStatus.READY,
            ProtectiveCoverageStatus.PARTIALLY_PROTECTED,
        } or not coverage.actionable:
            raise ValueError("coverage must be actionable and require protection.")
        if position.is_flat:
            raise ValueError("cannot protect a flat position.")
        if coverage.broker != position.broker or coverage.symbol != position.symbol:
            raise ValueError("coverage identity must match position.")
        if coverage.position_quantity != position.quantity:
            raise ValueError("coverage quantity must match position quantity.")
        if intent.symbol != position.symbol:
            raise ValueError("intent symbol must match position.")

        position_side = (
            "buy" if position.direction is PositionDirection.LONG else "sell"
        )
        if intent.side != position_side:
            raise ValueError("intent side must match position direction.")
        exit_side = "sell" if position_side == "buy" else "buy"
        self._validate_prices(intent=intent, position=position)

        quantity = coverage.uncovered_quantity
        if quantity <= 0:
            raise ValueError("coverage must contain uncovered quantity.")
        target1_quantity = (quantity + 1) // 2
        target2_quantity = quantity - target1_quantity
        slices = [
            ProtectedOrderSlice(
                label="target1",
                quantity=target1_quantity,
                stop_price=intent.stop_price,
                target_price=intent.target1_price,
            )
        ]
        warnings = coverage.warnings
        if target2_quantity:
            slices.append(
                ProtectedOrderSlice(
                    label="target2",
                    quantity=target2_quantity,
                    stop_price=intent.stop_price,
                    target_price=intent.target2_price,
                )
            )
        else:
            warnings += (
                "One uncovered share uses Target 1 only.",
            )
        return ExistingPositionProtectionPlan(
            broker=position.broker,
            symbol=position.symbol,
            position_side=position_side,
            exit_side=exit_side,
            position_quantity=position.quantity,
            protected_quantity=coverage.protected_quantity,
            uncovered_quantity=quantity,
            time_in_force=intent.time_in_force,
            position_updated_at=position.last_updated_at,
            slices=tuple(slices),
            valid=True,
            actionable=True,
            reasons=coverage.reasons,
            warnings=warnings,
        )

    @staticmethod
    def _validate_prices(
        *, intent: ExecutionOrderIntent, position: ExecutionPosition
    ) -> None:
        entry = position.average_entry_price
        if position.direction is PositionDirection.LONG:
            valid = (
                intent.stop_price < entry
                and intent.target1_price > entry
                and intent.target2_price >= intent.target1_price
            )
        else:
            valid = (
                intent.stop_price > entry
                and intent.target1_price < entry
                and intent.target2_price <= intent.target1_price
            )
        if not valid:
            raise ValueError(
                "stop and target prices do not protect the reconciled position."
            )
