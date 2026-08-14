from __future__ import annotations

from dataclasses import dataclass

from imie.models.concurrent_position_assessment import ConcurrentPositionAssessment
from imie.models.daily_loss_assessment import DailyLossAssessment
from imie.models.execution_safety_assessment import ExecutionSafetyAssessment
from imie.models.execution_submission_reservation import (
    ExecutionSubmissionReservation,
)
from imie.models.protected_plan_submission_result import (
    ProtectedPlanSubmissionResult,
)


@dataclass(frozen=True, slots=True)
class ProtectedExecutionSafetyResult:
    assessment: ExecutionSafetyAssessment
    protected_submission: ProtectedPlanSubmissionResult | None
    reservation: ExecutionSubmissionReservation | None = None
    concurrent_position_assessment: ConcurrentPositionAssessment | None = None
    daily_loss_assessment: DailyLossAssessment | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, ExecutionSafetyAssessment):
            raise TypeError("assessment must be an ExecutionSafetyAssessment.")
        for value, expected, name in (
            (
                self.protected_submission,
                ProtectedPlanSubmissionResult,
                "protected_submission",
            ),
            (self.reservation, ExecutionSubmissionReservation, "reservation"),
            (
                self.concurrent_position_assessment,
                ConcurrentPositionAssessment,
                "concurrent_position_assessment",
            ),
            (
                self.daily_loss_assessment,
                DailyLossAssessment,
                "daily_loss_assessment",
            ),
        ):
            if value is not None and not isinstance(value, expected):
                raise TypeError(f"{name} must be a {expected.__name__} or None.")
        allowed = self.assessment.allowed and (
            self.concurrent_position_assessment is None
            or self.concurrent_position_assessment.allowed
        )
        allowed = allowed and (
            self.daily_loss_assessment is None
            or self.daily_loss_assessment.allowed
        )
        if allowed != (self.protected_submission is not None):
            raise ValueError(
                "effective safety decision must match protected submission."
            )
        if allowed != (self.reservation is not None):
            raise ValueError("effective safety decision must match reservation.")
        for value, label in (
            (self.protected_submission, "protected submission"),
            (self.reservation, "reservation"),
            (self.concurrent_position_assessment, "concurrent assessment"),
        ):
            if value is not None and value.symbol != self.assessment.symbol:
                raise ValueError(f"{label} symbol must match safety assessment.")

    @property
    def submitted(self) -> bool:
        return self.protected_submission is not None
