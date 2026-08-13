from __future__ import annotations

from typing import Protocol

from imie.models import (
    ProtectedExecutionPlan,
    ProtectedPlanSubmissionResult,
)


class ProtectedExecutionPort(Protocol):
    def submit_protected_plan(
        self,
        plan: ProtectedExecutionPlan,
    ) -> ProtectedPlanSubmissionResult:
        ...
