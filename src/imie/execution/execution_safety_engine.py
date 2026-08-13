from __future__ import annotations

from imie.models import (
    ExecutionCandidate,
    ExecutionSafetyAssessment,
    ExecutionSafetyPolicy,
)


class ExecutionSafetyEngine:
    """Evaluate pre-submission financial limits without broker mutation."""

    def assess(
        self,
        *,
        candidate: ExecutionCandidate,
        policy: ExecutionSafetyPolicy,
    ) -> ExecutionSafetyAssessment:
        if not isinstance(candidate, ExecutionCandidate):
            raise TypeError("candidate must be an ExecutionCandidate.")
        if not isinstance(policy, ExecutionSafetyPolicy):
            raise TypeError("policy must be an ExecutionSafetyPolicy.")

        violations: list[str] = []
        warnings: list[str] = list(candidate.warnings)
        notional_within_limit = (
            candidate.position_notional <= policy.maximum_order_notional
        )
        risk_within_limit = candidate.risk_amount <= policy.maximum_risk_amount
        if not notional_within_limit:
            violations.append(
                "Order notional exceeds maximum: "
                f"{candidate.position_notional:.2f} > "
                f"{policy.maximum_order_notional:.2f}."
            )
        if not risk_within_limit:
            violations.append(
                "Trade risk exceeds maximum: "
                f"{candidate.risk_amount:.2f} > "
                f"{policy.maximum_risk_amount:.2f}."
            )
        if not candidate.valid:
            violations.append("Execution candidate is invalid.")
        if not candidate.actionable:
            violations.append("Execution candidate is not actionable.")
        if policy.kill_switch_active:
            violations.append("Execution kill switch is active.")
        limits_pass = notional_within_limit and risk_within_limit
        allowed = (
            limits_pass
            and candidate.valid
            and candidate.actionable
            and not policy.kill_switch_active
        )
        return ExecutionSafetyAssessment(
            symbol=candidate.symbol,
            order_notional=candidate.position_notional,
            risk_amount=candidate.risk_amount,
            maximum_order_notional=policy.maximum_order_notional,
            maximum_risk_amount=policy.maximum_risk_amount,
            candidate_valid=candidate.valid,
            candidate_actionable=candidate.actionable,
            notional_within_limit=notional_within_limit,
            risk_within_limit=risk_within_limit,
            allowed=allowed,
            kill_switch_active=policy.kill_switch_active,
            violations=tuple(violations),
            warnings=tuple(warnings),
        )
