from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import (
    ExecutionPosition,
    ExistingPositionProtectionPlan,
    ExistingPositionProtectionResult,
)


@runtime_checkable
class ExistingPositionProtectionPort(Protocol):
    """Broker boundary for exit protection on an existing position."""

    def submit_existing_position_protection(
        self,
        *,
        plan: ExistingPositionProtectionPlan,
        current_position: ExecutionPosition,
    ) -> ExistingPositionProtectionResult:
        """Submit only after verifying current_position still matches plan."""
        ...
