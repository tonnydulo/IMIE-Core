from __future__ import annotations

import math

from datetime import datetime, timezone
from typing import Callable

from imie.execution.broker_execution_port import BrokerExecutionPort
from imie.execution.execution_safety_engine import ExecutionSafetyEngine
from imie.execution.execution_submission_fingerprint import (
    ExecutionSubmissionFingerprint,
)
from imie.execution.execution_submission_reservation_store import (
    ExecutionSubmissionReservationStore,
)
from imie.execution.broker_position_exposure_port import (
    BrokerPositionExposurePort,
)
from imie.execution.concurrent_position_safety_engine import (
    ConcurrentPositionSafetyEngine,
)
from imie.models import (
    BrokerSubmissionResult,
    ExecutionCandidate,
    ExecutionOrderIntent,
    ExecutionSafetyPolicy,
    ExecutionSafetySubmissionResult,
    ExecutionSubmissionReservation,
)


class ExecutionSafetySubmissionService:
    """Fail closed before forwarding an order intent to a broker port."""

    def __init__(
        self,
        *,
        broker_execution_port: BrokerExecutionPort,
        policy: ExecutionSafetyPolicy,
        reservation_store: ExecutionSubmissionReservationStore,
        engine: ExecutionSafetyEngine | None = None,
        clock: Callable[[], datetime] | None = None,
        position_exposure_port: BrokerPositionExposurePort | None = None,
        maximum_concurrent_positions: int | None = None,
        concurrent_position_engine: ConcurrentPositionSafetyEngine | None = None,
    ) -> None:
        if not isinstance(broker_execution_port, BrokerExecutionPort):
            raise TypeError(
                "broker_execution_port must satisfy BrokerExecutionPort."
            )
        if not isinstance(policy, ExecutionSafetyPolicy):
            raise TypeError("policy must be an ExecutionSafetyPolicy.")
        if not isinstance(
            reservation_store, ExecutionSubmissionReservationStore
        ):
            raise TypeError(
                "reservation_store must satisfy "
                "ExecutionSubmissionReservationStore."
            )
        resolved_engine = engine or ExecutionSafetyEngine()
        if not isinstance(resolved_engine, ExecutionSafetyEngine):
            raise TypeError("engine must be an ExecutionSafetyEngine or None.")
        self._broker_execution_port = broker_execution_port
        self._policy = policy
        self._reservation_store = reservation_store
        self._engine = resolved_engine
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        self._clock = resolved_clock
        if (position_exposure_port is None) != (
            maximum_concurrent_positions is None
        ):
            raise ValueError(
                "position_exposure_port and maximum_concurrent_positions "
                "must be configured together."
            )
        if position_exposure_port is not None and not isinstance(
            position_exposure_port, BrokerPositionExposurePort
        ):
            raise TypeError(
                "position_exposure_port must satisfy "
                "BrokerPositionExposurePort."
            )
        if maximum_concurrent_positions is not None and (
            isinstance(maximum_concurrent_positions, bool)
            or not isinstance(maximum_concurrent_positions, int)
        ):
            raise TypeError("maximum_concurrent_positions must be an int or None.")
        if (
            maximum_concurrent_positions is not None
            and maximum_concurrent_positions <= 0
        ):
            raise ValueError("maximum_concurrent_positions must be positive.")
        resolved_concurrent_engine = (
            concurrent_position_engine or ConcurrentPositionSafetyEngine()
        )
        if not isinstance(
            resolved_concurrent_engine, ConcurrentPositionSafetyEngine
        ):
            raise TypeError(
                "concurrent_position_engine must be a "
                "ConcurrentPositionSafetyEngine or None."
            )
        self._position_exposure_port = position_exposure_port
        self._maximum_concurrent_positions = maximum_concurrent_positions
        self._concurrent_position_engine = resolved_concurrent_engine

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
                reservation=None,
            )
        concurrent_assessment = None
        if self._position_exposure_port is not None:
            exposure = self._position_exposure_port.get_open_position_exposure()
            concurrent_assessment = self._concurrent_position_engine.assess(
                symbol=intent.symbol,
                exposure=exposure,
                maximum_concurrent_positions=(
                    self._maximum_concurrent_positions
                ),
            )
            if not concurrent_assessment.allowed:
                return ExecutionSafetySubmissionResult(
                    assessment=assessment,
                    concurrent_position_assessment=concurrent_assessment,
                    broker_submission=None,
                    reservation=None,
                )
        fingerprint = ExecutionSubmissionFingerprint.create(
            candidate=candidate,
            intent=intent,
        )
        reserved_at = self._clock()
        if not isinstance(reserved_at, datetime):
            raise TypeError("clock must return a datetime.")
        if reserved_at.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        reservation = ExecutionSubmissionReservation(
            fingerprint=fingerprint,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            reserved_at=reserved_at,
        )
        self._reservation_store.reserve(reservation)
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
            reservation=reservation,
            concurrent_position_assessment=concurrent_assessment,
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
