from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import (
    ProtectedExecutionPlan,
    ProtectedPlanSubmissionResult,
)


@runtime_checkable
class ProtectedExecutionPort(Protocol):
    def submit_protected_plan(
        self,
        plan: ProtectedExecutionPlan,
    ) -> ProtectedPlanSubmissionResult:
        ...
