from imie.models import (
    DecisionResult,
    ExecutionCandidate,
    PositionSizeResult,
)


class ExecutionCandidateBuilder:
    def build(
        self,
        *,
        decision: DecisionResult,
        position_size: PositionSizeResult,
    ) -> ExecutionCandidate:
        if not isinstance(
            decision,
            DecisionResult,
        ):
            raise TypeError(
                "decision must be a DecisionResult."
            )

        if not isinstance(
            position_size,
            PositionSizeResult,
        ):
            raise TypeError(
                "position_size must be a PositionSizeResult."
            )

        trade_plan = decision.trade_plan

        if (
            not decision.actionable
            or trade_plan is None
            or not trade_plan.actionable
        ):
            raise ValueError(
                "Decision must contain an actionable "
                "TradePlan."
            )

        if decision.decision.value != "READY":
            raise ValueError(
                "Decision must be READY."
            )

        if trade_plan.entry is None:
            raise ValueError(
                "TradePlan entry is required."
            )

        if trade_plan.stop is None:
            raise ValueError(
                "TradePlan stop is required."
            )

        if trade_plan.target1 is None:
            raise ValueError(
                "TradePlan target1 is required."
            )

        if trade_plan.target2 is None:
            raise ValueError(
                "TradePlan target2 is required."
            )

        if trade_plan.symbol != position_size.symbol:
            raise ValueError(
                "TradePlan and PositionSizeResult "
                "symbols must match."
            )

        if trade_plan.direction != position_size.direction:
            raise ValueError(
                "TradePlan and PositionSizeResult "
                "directions must match."
            )

        actionable = (
            decision.actionable
            and trade_plan.actionable
            and position_size.actionable
            and position_size.quantity > 0
        )

        reasons = (
            tuple(decision.reasons)
            + tuple(trade_plan.reasons)
            + tuple(position_size.reasons)
        )

        warnings = (
            tuple(decision.warnings)
            + tuple(trade_plan.warnings)
            + tuple(position_size.warnings)
        )

        return ExecutionCandidate(
            symbol=trade_plan.symbol,
            strategy=trade_plan.strategy,
            direction=trade_plan.direction,
            quantity=position_size.quantity,
            entry=trade_plan.entry,
            stop=trade_plan.stop,
            target1=trade_plan.target1,
            target2=trade_plan.target2,
            position_notional=(
                position_size.position_notional
            ),
            risk_amount=position_size.actual_risk,
            valid=(
                trade_plan.valid
                and position_size.valid
            ),
            actionable=actionable,
            reasons=reasons,
            warnings=warnings,
        )