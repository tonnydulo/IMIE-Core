from __future__ import annotations

from imie.execution.broker_position_protection_validator import (
    BrokerPositionProtectionValidator,
)
from imie.execution.broker_position_query_port import BrokerPositionQueryPort
from imie.execution.existing_position_protection_port import (
    ExistingPositionProtectionPort,
)
from imie.execution.position_state_store import PositionStateStore
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    ExistingPositionProtectionResult,
)


class ExistingPositionProtectionService:
    """Explicitly validate two position truths before protective mutation."""

    def __init__(
        self,
        *,
        position_store: PositionStateStore,
        position_query_port: BrokerPositionQueryPort,
        protection_port: ExistingPositionProtectionPort,
        validator: BrokerPositionProtectionValidator | None = None,
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
        self._validator = resolved_validator

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
        result = self._protection_port.submit_existing_position_protection(
            plan=plan,
            current_position=validated_position,
        )
        if not isinstance(result, ExistingPositionProtectionResult):
            raise TypeError(
                "protection_port must return ExistingPositionProtectionResult."
            )
        if result.broker != plan.broker or result.symbol != plan.symbol:
            raise ValueError("Protection result identity does not match plan.")
        if result.position_updated_at != plan.position_updated_at:
            raise ValueError("Protection result position timestamp does not match plan.")
        if result.requested_quantity != plan.uncovered_quantity:
            raise ValueError("Protection result quantity does not match plan.")
        return result
