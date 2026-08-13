from __future__ import annotations

from imie.execution.broker_position_protection_validator import (
    BrokerPositionProtectionValidator,
)
from imie.execution.broker_position_query_port import BrokerPositionQueryPort
from imie.execution.existing_position_protection_port import (
    ExistingPositionProtectionPort,
)
from imie.execution.position_state_store import PositionStateStore
from imie.execution.position_protection_store import PositionProtectionStore
from imie.execution.position_protection_attempt_store import (
    PositionProtectionAttemptStore,
)
from imie.execution.protection_audit_persistence_error import (
    ProtectionAuditPersistenceError,
)
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    ExistingPositionProtectionResult,
    PositionProtectionRecord,
    PositionProtectionAttempt,
    PositionProtectionAttemptStatus,
)


class ExistingPositionProtectionService:
    """Explicitly validate two position truths before protective mutation."""

    def __init__(
        self,
        *,
        position_store: PositionStateStore,
        position_query_port: BrokerPositionQueryPort,
        protection_port: ExistingPositionProtectionPort,
        protection_store: PositionProtectionStore,
        attempt_store: PositionProtectionAttemptStore,
        validator: BrokerPositionProtectionValidator | None = None,
        clock: Callable[[], datetime] | None = None,
        attempt_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(position_store, PositionStateStore):
            raise TypeError("position_store must satisfy PositionStateStore.")
        if not isinstance(position_query_port, BrokerPositionQueryPort):
            raise TypeError(
                "position_query_port must satisfy BrokerPositionQueryPort."
            )
        if not isinstance(protection_port, ExistingPositionProtectionPort):
            raise TypeError(
                "protection_port must satisfy ExistingPositionProtectionPort."
            )
        if not isinstance(protection_store, PositionProtectionStore):
            raise TypeError(
                "protection_store must satisfy PositionProtectionStore."
            )
        if not isinstance(attempt_store, PositionProtectionAttemptStore):
            raise TypeError(
                "attempt_store must satisfy PositionProtectionAttemptStore."
            )
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        resolved_attempt_id_factory = attempt_id_factory or (
            lambda: uuid4().hex
        )
        if not callable(resolved_attempt_id_factory):
            raise TypeError("attempt_id_factory must be callable or None.")
        resolved_validator = validator or BrokerPositionProtectionValidator()
        if not isinstance(
            resolved_validator, BrokerPositionProtectionValidator
        ):
            raise TypeError(
                "validator must be a BrokerPositionProtectionValidator or None."
            )
        self._position_store = position_store
        self._position_query_port = position_query_port
        self._protection_port = protection_port
        self._protection_store = protection_store
        self._attempt_store = attempt_store
        self._validator = resolved_validator
        self._clock = resolved_clock
        self._attempt_id_factory = resolved_attempt_id_factory

    def protect(
        self,
        plan: ExistingPositionProtectionPlan,
    ) -> ExistingPositionProtectionResult:
        if not isinstance(plan, ExistingPositionProtectionPlan):
            raise TypeError("plan must be an ExistingPositionProtectionPlan.")
        recorded_position = self._position_store.get(
            broker=plan.broker,
            symbol=plan.symbol,
        )
        if recorded_position is None:
            raise LookupError(
                "No persisted position exists for the protection plan."
            )
        if not isinstance(recorded_position, ExecutionPosition):
            raise TypeError(
                "position_store.get() must return ExecutionPosition or None."
            )

        prior = self._protection_store.get_for_position(
            broker=plan.broker,
            symbol=plan.symbol,
            position_updated_at=plan.position_updated_at,
            position_fill_ids=plan.position_fill_ids,
        )
        if prior is not None:
            if not isinstance(prior, PositionProtectionRecord):
                raise TypeError(
                    "protection_store.get_for_position() must return "
                    "PositionProtectionRecord or None."
                )
            raise RuntimeError(
                "Accepted protection already exists for this position fingerprint."
            )
        prior_attempt = self._attempt_store.get_for_position(
            broker=plan.broker,
            symbol=plan.symbol,
            position_updated_at=plan.position_updated_at,
            position_fill_ids=plan.position_fill_ids,
        )
        if prior_attempt is not None:
            if not isinstance(prior_attempt, PositionProtectionAttempt):
                raise TypeError(
                    "attempt_store.get_for_position() must return "
                    "PositionProtectionAttempt or None."
                )
            raise RuntimeError(
                "A protection attempt already exists for this position "
                f"fingerprint with status {prior_attempt.status.value}."
            )

        broker_position = self._position_query_port.get_position(plan.symbol)
        if broker_position is not None and not isinstance(
            broker_position, BrokerPositionSnapshot
        ):
            raise TypeError(
                "position_query_port.get_position() must return "
                "BrokerPositionSnapshot or None."
            )
        validated_position = self._validator.validate(
            plan=plan,
            recorded_position=recorded_position,
            broker_position=broker_position,
        )
        reserved_at = self._now()
        attempt = PositionProtectionAttempt(
            attempt_id=self._attempt_id_factory(),
            broker=plan.broker,
            symbol=plan.symbol,
            position_updated_at=plan.position_updated_at,
            position_fill_ids=plan.position_fill_ids,
            status=PositionProtectionAttemptStatus.RESERVED,
            created_at=reserved_at,
            updated_at=reserved_at,
            message="Position protection attempt reserved before broker mutation.",
        )
        self._attempt_store.reserve(attempt)
        try:
            result = self._protection_port.submit_existing_position_protection(
                plan=plan,
                current_position=validated_position,
            )
        except Exception as exc:
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.UNCERTAIN,
                message=f"Broker protection outcome is uncertain: {exc}",
            )
            raise
        if not isinstance(result, ExistingPositionProtectionResult):
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.UNCERTAIN,
                message="Broker returned an invalid protection result type.",
            )
            raise TypeError(
                "protection_port must return ExistingPositionProtectionResult."
            )
        if result.broker != plan.broker or result.symbol != plan.symbol:
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.UNCERTAIN,
                message="Broker returned mismatched protection identity.",
            )
            raise ValueError("Protection result identity does not match plan.")
        if result.position_updated_at != plan.position_updated_at:
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.UNCERTAIN,
                message="Broker returned a mismatched position timestamp.",
            )
            raise ValueError("Protection result position timestamp does not match plan.")
        if result.requested_quantity != plan.uncovered_quantity:
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.UNCERTAIN,
                message="Broker returned a mismatched protection quantity.",
                result=result,
            )
            raise ValueError("Protection result quantity does not match plan.")
        if result.accepted:
            recorded_at = self._now()
            try:
                self._protection_store.save(
                    PositionProtectionRecord(
                        result=result,
                        position_fill_ids=plan.position_fill_ids,
                        recorded_at=recorded_at,
                    )
                )
            except Exception as exc:
                self._transition_attempt(
                    attempt=attempt,
                    status=PositionProtectionAttemptStatus.UNCERTAIN,
                    message=(
                        "Broker accepted protection, but its audit record "
                        f"could not be persisted: {exc}"
                    ),
                    result=result,
                )
                raise ProtectionAuditPersistenceError(
                    result=result,
                    cause=exc,
                ) from exc
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.ACCEPTED,
                message="Broker protection accepted and audit record persisted.",
                result=result,
            )
        else:
            self._transition_attempt(
                attempt=attempt,
                status=PositionProtectionAttemptStatus.FAILED,
                message=(
                    "Broker protection was not accepted; no accepted audit "
                    "record was created."
                ),
                result=result,
            )
        return result

    def _transition_attempt(
        self,
        *,
        attempt: PositionProtectionAttempt,
        status: PositionProtectionAttemptStatus,
        message: str,
        result: ExistingPositionProtectionResult | None = None,
    ) -> None:
        self._attempt_store.transition(
            PositionProtectionAttempt(
                attempt_id=attempt.attempt_id,
                broker=attempt.broker,
                symbol=attempt.symbol,
                position_updated_at=attempt.position_updated_at,
                position_fill_ids=attempt.position_fill_ids,
                status=status,
                created_at=attempt.created_at,
                updated_at=self._now(),
                message=message,
                result=result,
            )
        )

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime):
            raise TypeError("clock must return a datetime.")
        if value.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        return value
