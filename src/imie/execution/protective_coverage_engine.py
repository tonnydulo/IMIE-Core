from __future__ import annotations

from imie.models import (
    ExecutionOrderIntent,
    ExecutionPosition,
    PositionDirection,
    ProtectedPlanSubmissionResult,
    ProtectiveCoverageAssessment,
    ProtectiveCoverageStatus,
)


class ProtectiveCoverageEngine:
    """Assess reconciled position coverage without submitting broker orders."""

    def assess(
        self,
        *,
        intent: ExecutionOrderIntent,
        position: ExecutionPosition | None,
        submission: ProtectedPlanSubmissionResult | None = None,
    ) -> ProtectiveCoverageAssessment:
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        if position is not None and not isinstance(position, ExecutionPosition):
            raise TypeError("position must be an ExecutionPosition or None.")
        if submission is not None and not isinstance(
            submission, ProtectedPlanSubmissionResult
        ):
            raise TypeError(
                "submission must be a ProtectedPlanSubmissionResult or None."
            )

        if position is None:
            return self._result(
                broker=None,
                symbol=intent.symbol,
                status=ProtectiveCoverageStatus.NO_POSITION,
                quantity=0,
                covered=0,
                actionable=False,
                reason="No reconciled position exists.",
            )
        if position.is_flat:
            return self._result(
                broker=position.broker,
                symbol=position.symbol,
                status=ProtectiveCoverageStatus.FLAT,
                quantity=0,
                covered=0,
                actionable=False,
                reason="The reconciled position is flat.",
            )

        expected_side = (
            "buy" if position.direction is PositionDirection.LONG else "sell"
        )
        mismatches = []
        if intent.symbol != position.symbol:
            mismatches.append("Intent symbol does not match the position.")
        if intent.side != expected_side:
            mismatches.append("Intent side does not match position direction.")
        if position.quantity > intent.quantity:
            mismatches.append("Position quantity exceeds planned intent quantity.")
        if submission is not None and submission.accepted:
            if submission.broker != position.broker:
                mismatches.append("Protected submission broker does not match position.")
            if submission.symbol != position.symbol:
                mismatches.append("Protected submission symbol does not match position.")
            if submission.side != expected_side:
                mismatches.append(
                    "Protected submission side does not match position direction."
                )
        if mismatches:
            return ProtectiveCoverageAssessment(
                broker=position.broker,
                symbol=position.symbol,
                status=ProtectiveCoverageStatus.MISMATCH,
                position_quantity=position.quantity,
                protected_quantity=0,
                uncovered_quantity=position.quantity,
                actionable=False,
                reasons=tuple(mismatches),
            )

        covered = (
            min(position.quantity, submission.quantity)
            if submission is not None and submission.accepted
            else 0
        )
        if covered == position.quantity:
            status = ProtectiveCoverageStatus.PROTECTED
            reason = "Accepted protective coverage spans the open position."
            actionable = False
        elif covered:
            status = ProtectiveCoverageStatus.PARTIALLY_PROTECTED
            reason = "Part of the open position lacks accepted protective coverage."
            actionable = True
        else:
            status = ProtectiveCoverageStatus.READY
            reason = "The open position is eligible for protective management."
            actionable = True
        warnings = ()
        if submission is not None and not submission.accepted:
            warnings = ("The prior protected submission was not accepted.",)
        return ProtectiveCoverageAssessment(
            broker=position.broker,
            symbol=position.symbol,
            status=status,
            position_quantity=position.quantity,
            protected_quantity=covered,
            uncovered_quantity=position.quantity - covered,
            actionable=actionable,
            reasons=(reason,),
            warnings=warnings,
        )

    @staticmethod
    def _result(
        *, broker, symbol, status, quantity, covered, actionable, reason
    ) -> ProtectiveCoverageAssessment:
        return ProtectiveCoverageAssessment(
            broker=broker,
            symbol=symbol,
            status=status,
            position_quantity=quantity,
            protected_quantity=covered,
            uncovered_quantity=quantity - covered,
            actionable=actionable,
            reasons=(reason,),
        )
