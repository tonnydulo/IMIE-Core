from __future__ import annotations

import math

from datetime import datetime

from imie.models import (
    PositionProtectionMonitoringAssessment,
    PositionProtectionReconciliationRecord,
)


class PositionProtectionMonitoringEngine:
    """Assess whether locally observed protection truth is current and healthy."""

    def __init__(self, *, maximum_age_seconds: float = 30.0) -> None:
        if isinstance(maximum_age_seconds, bool) or not isinstance(
            maximum_age_seconds, int | float
        ):
            raise TypeError("maximum_age_seconds must be a number.")
        maximum_age_seconds = float(maximum_age_seconds)
        if not math.isfinite(maximum_age_seconds) or maximum_age_seconds <= 0:
            raise ValueError("maximum_age_seconds must be finite and positive.")
        self.maximum_age_seconds = maximum_age_seconds

    def assess(
        self,
        *,
        broker: str,
        symbol: str,
        record: PositionProtectionReconciliationRecord | None,
        checked_at: datetime,
    ) -> PositionProtectionMonitoringAssessment:
        if not isinstance(checked_at, datetime) or checked_at.tzinfo is None:
            raise ValueError("checked_at must be a timezone-aware datetime.")
        if record is None:
            return self._result(
                broker=broker,
                symbol=symbol,
                state="never_observed",
                checked_at=checked_at,
                reason="Broker protection truth has never been observed.",
            )
        if not isinstance(record, PositionProtectionReconciliationRecord):
            raise TypeError(
                "record must be PositionProtectionReconciliationRecord or None."
            )
        if record.result.broker != broker.strip().lower():
            raise ValueError("record broker does not match assessment broker.")
        if record.result.symbol != symbol.strip().upper():
            raise ValueError("record symbol does not match assessment symbol.")
        age = (checked_at - record.observed_at).total_seconds()
        if age < 0:
            return self._result(
                broker=broker,
                symbol=symbol,
                state="fresh_unhealthy",
                checked_at=checked_at,
                record=record,
                age=0.0,
                reason="Protection observation timestamp is in the future.",
                warnings=("Clock alignment must be verified.",),
            )
        if age > self.maximum_age_seconds:
            return self._result(
                broker=broker,
                symbol=symbol,
                state="stale",
                checked_at=checked_at,
                record=record,
                age=age,
                reason="Latest broker protection truth is stale.",
            )
        if record.result.state == "active" and record.result.reconciled:
            return self._result(
                broker=broker,
                symbol=symbol,
                state="fresh_healthy",
                checked_at=checked_at,
                record=record,
                age=age,
                healthy=True,
                action_required=False,
                reason="Fresh broker truth confirms active protective coverage.",
            )
        return self._result(
            broker=broker,
            symbol=symbol,
            state="fresh_unhealthy",
            checked_at=checked_at,
            record=record,
            age=age,
            reason=(
                "Fresh broker truth requires review: "
                f"{record.result.state}."
            ),
            warnings=record.result.warnings,
        )

    def _result(
        self,
        *,
        broker: str,
        symbol: str,
        state: str,
        checked_at: datetime,
        reason: str,
        record: PositionProtectionReconciliationRecord | None = None,
        age: float | None = None,
        healthy: bool = False,
        action_required: bool = True,
        warnings: tuple[str, ...] = (),
    ) -> PositionProtectionMonitoringAssessment:
        return PositionProtectionMonitoringAssessment(
            broker=broker,
            symbol=symbol,
            state=state,
            checked_at=checked_at,
            observed_at=record.observed_at if record else None,
            observation_age_seconds=age,
            maximum_age_seconds=self.maximum_age_seconds,
            reconciliation_state=record.result.state if record else None,
            healthy=healthy,
            action_required=action_required,
            reason=reason,
            warnings=warnings,
        )
