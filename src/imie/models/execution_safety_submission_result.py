from __future__ import annotations

from dataclasses import dataclass

from imie.models.broker_submission_result import BrokerSubmissionResult
from imie.models.execution_safety_assessment import ExecutionSafetyAssessment
from imie.models.execution_submission_reservation import (
    ExecutionSubmissionReservation,
)
from imie.models.concurrent_position_assessment import (
    ConcurrentPositionAssessment,
)


@dataclass(frozen=True, slots=True)
class ExecutionSafetySubmissionResult:
    assessment: ExecutionSafetyAssessment
    broker_submission: BrokerSubmissionResult | None
    reservation: ExecutionSubmissionReservation | None = None
    concurrent_position_assessment: ConcurrentPositionAssessment | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, ExecutionSafetyAssessment):
            raise TypeError("assessment must be an ExecutionSafetyAssessment.")
        if self.broker_submission is not None and not isinstance(
            self.broker_submission, BrokerSubmissionResult
        ):
            raise TypeError(
                "broker_submission must be a BrokerSubmissionResult or None."
            )
        if self.reservation is not None and not isinstance(
            self.reservation, ExecutionSubmissionReservation
        ):
            raise TypeError(
                "reservation must be an ExecutionSubmissionReservation or None."
            )
        if (
            self.concurrent_position_assessment is not None
            and not isinstance(
                self.concurrent_position_assessment,
                ConcurrentPositionAssessment,
            )
        ):
            raise TypeError(
                "concurrent_position_assessment must be a "
                "ConcurrentPositionAssessment or None."
            )
        effectively_allowed = self.assessment.allowed and (
            self.concurrent_position_assessment is None
            or self.concurrent_position_assessment.allowed
        )
        if not effectively_allowed and self.broker_submission is not None:
            raise ValueError("blocked safety assessment cannot have broker submission.")
        if effectively_allowed and self.broker_submission is None:
            raise ValueError("allowed safety assessment requires broker submission.")
        if not effectively_allowed and self.reservation is not None:
            raise ValueError("blocked safety assessment cannot have reservation.")
        if effectively_allowed and self.reservation is None:
            raise ValueError("allowed safety assessment requires reservation.")
        if self.broker_submission is not None and (
            self.broker_submission.symbol != self.assessment.symbol
        ):
            raise ValueError("broker submission symbol must match safety assessment.")
        if self.reservation is not None and (
            self.reservation.symbol != self.assessment.symbol
        ):
            raise ValueError("reservation symbol must match safety assessment.")
        if self.concurrent_position_assessment is not None and (
            self.concurrent_position_assessment.symbol != self.assessment.symbol
        ):
            raise ValueError(
                "concurrent position symbol must match safety assessment."
            )

    @property
    def submitted(self) -> bool:
        return self.broker_submission is not None
