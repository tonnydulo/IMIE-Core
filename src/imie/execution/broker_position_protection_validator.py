from __future__ import annotations

import math

from datetime import datetime, timedelta, timezone
from typing import Callable

from imie.execution.existing_position_protection_guard import (
    ExistingPositionProtectionGuard,
)
from imie.models import (
    BrokerPositionSnapshot,
    ExecutionPosition,
    ExistingPositionProtectionPlan,
)


class BrokerPositionProtectionValidator:
    """Validate an IMIE protection plan against fresh broker position truth."""

    def __init__(
        self,
        *,
        maximum_snapshot_age: timedelta = timedelta(seconds=5),
        clock: Callable[[], datetime] | None = None,
        guard: ExistingPositionProtectionGuard | None = None,
    ) -> None:
        if not isinstance(maximum_snapshot_age, timedelta):
            raise TypeError("maximum_snapshot_age must be a timedelta.")
        if maximum_snapshot_age <= timedelta(0):
            raise ValueError("maximum_snapshot_age must be positive.")
        resolved_clock = clock or (lambda: datetime.now(timezone.utc))
        if not callable(resolved_clock):
            raise TypeError("clock must be callable or None.")
        resolved_guard = guard or ExistingPositionProtectionGuard()
        if not isinstance(resolved_guard, ExistingPositionProtectionGuard):
            raise TypeError(
                "guard must be an ExistingPositionProtectionGuard or None."
            )
        self._maximum_snapshot_age = maximum_snapshot_age
        self._clock = resolved_clock
        self._guard = resolved_guard

    def validate(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        recorded_position: ExecutionPosition,
        broker_position: BrokerPositionSnapshot | None,
    ) -> ExecutionPosition:
        self._guard.validate(
            plan=plan,
            current_position=recorded_position,
        )
        if broker_position is None:
            raise ValueError("Broker reports no open position; protection is stale.")
        if not isinstance(broker_position, BrokerPositionSnapshot):
            raise TypeError(
                "broker_position must be a BrokerPositionSnapshot or None."
            )

        now = self._clock()
        if not isinstance(now, datetime):
            raise TypeError("clock must return a datetime.")
        if now.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime.")
        age = now - broker_position.observed_at
        if age < timedelta(0):
            raise ValueError("Broker position snapshot cannot be from the future.")
        if age > self._maximum_snapshot_age:
            raise ValueError("Broker position snapshot is stale.")

        comparisons = (
            (broker_position.broker == plan.broker, "broker"),
            (broker_position.symbol == plan.symbol, "symbol"),
            (
                broker_position.direction == recorded_position.direction,
                "direction",
            ),
            (
                broker_position.quantity == recorded_position.quantity,
                "quantity",
            ),
        )
        for matched, name in comparisons:
            if not matched:
                raise ValueError(
                    f"Fresh broker position {name} does not match protection plan."
                )
        if not math.isclose(
            broker_position.average_entry_price,
            recorded_position.average_entry_price,
            rel_tol=1e-9,
            abs_tol=0.0001,
        ):
            raise ValueError(
                "Fresh broker average entry does not match recorded position."
            )
        if plan.uncovered_quantity > broker_position.quantity:
            raise ValueError(
                "Protection quantity exceeds fresh broker position quantity."
            )
        return recorded_position
