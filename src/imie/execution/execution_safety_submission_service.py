from __future__ import annotations

import math

from imie.execution.broker_execution_port import BrokerExecutionPort
from imie.execution.execution_safety_engine import ExecutionSafetyEngine
from imie.models import (
    BrokerSubmissionResult,
    ExecutionCandidate,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
    ExecutionSafetySubmissionResult,
)


class ExecutionSafetySubmissionService:
    """Fail closed before forwarding an order intent to a broker port."""

    def __init__(
        self,
        *,
        broker_execution_port: BrokerExecutionPort,
        policy: ExecutionSafetyPolicy,
        engine: ExecutionSafetyEngine | None = None,
    ) -> None:
        if not isinstance(broker_execution_port, BrokerExecutionPort):
            raise TypeError(
                "broker_execution_port must satisfy BrokerExecutionPort."
            )
        if not isinstance(policy, ExecutionSafetyPolicy):
            raise TypeError("policy must be an ExecutionSafetyPolicy.")
        resolved_engine = engine or ExecutionSafetyEngine()
        if not isinstance(resolved_engine, ExecutionSafetyEngine):
            raise TypeError("engine must be an ExecutionSafetyEngine or None.")
        self._broker_execution_port = broker_execution_port
        self._policy = policy
        self._engine = resolved_engine

    def submit(
        self,
        *,
        candidate: ExecutionCandidate,
        intent: ExecutionOrderIntent,
    ) -> ExecutionSafetySubmissionResult:
        if not isinstance(candidate, ExecutionCandidate):
            raise TypeError("candidate must be an ExecutionCandidate.")
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        self._validate_mapping(candidate=candidate, intent=intent)
        assessment = self._engine.assess(
            candidate=candidate,
            policy=self._policy,
        )
        if not assessment.allowed:
            return ExecutionSafetySubmissionResult(
                assessment=assessment,
                broker_submission=None,
            )
        submission = self._broker_execution_port.submit_order(intent)
        if not isinstance(submission, BrokerSubmissionResult):
            raise TypeError(
                "broker_execution_port.submit_order() must return "
                "BrokerSubmissionResult."
            )
        if (
            submission.symbol != intent.symbol
            or submission.side != intent.side
            or submission.quantity != intent.quantity
        ):
            raise ValueError("Broker submission identity does not match order intent.")
        return ExecutionSafetySubmissionResult(
            assessment=assessment,
            broker_submission=submission,
        )

    @staticmethod
    def _validate_mapping(
        *, candidate: ExecutionCandidate, intent: ExecutionOrderIntent
    ) -> None:
        expected_side = "buy" if candidate.direction == "long" else "sell"
        mismatches = []
        for label, expected, actual in (
            ("symbol", candidate.symbol, intent.symbol),
            ("side", expected_side, intent.side),
            ("quantity", candidate.quantity, intent.quantity),
        ):
            if expected != actual:
                mismatches.append(label)
        for label, expected, actual in (
            ("stop", candidate.stop, intent.stop_price),
            ("target1", candidate.target1, intent.target1_price),
            ("target2", candidate.target2, intent.target2_price),
        ):
            if not math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-6):
                mismatches.append(label)
        if intent.order_type == "limit" and (
            intent.entry_price is None
            or not math.isclose(
                candidate.entry,
                intent.entry_price,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            mismatches.append("entry")
        if candidate.valid != intent.valid:
            mismatches.append("valid")
        if candidate.actionable != intent.actionable:
            mismatches.append("actionable")
        if mismatches:
            raise ValueError(
                "Execution candidate and order intent do not match: "
                + ", ".join(mismatches)
                + "."
            )
