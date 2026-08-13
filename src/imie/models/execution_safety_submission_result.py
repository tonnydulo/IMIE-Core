from __future__ import annotations

from dataclasses import dataclass

from imie.models.broker_submission_result import BrokerSubmissionResult
from imie.models.execution_safety_assessment import ExecutionSafetyAssessment


@dataclass(frozen=True, slots=True)
class ExecutionSafetySubmissionResult:
    assessment: ExecutionSafetyAssessment
    broker_submission: BrokerSubmissionResult | None

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, ExecutionSafetyAssessment):
            raise TypeError("assessment must be an ExecutionSafetyAssessment.")
        if self.broker_submission is not None and not isinstance(
            self.broker_submission, BrokerSubmissionResult
        ):
            raise TypeError(
                "broker_submission must be a BrokerSubmissionResult or None."
            )
        if not self.assessment.allowed and self.broker_submission is not None:
            raise ValueError("blocked safety assessment cannot have broker submission.")
        if self.assessment.allowed and self.broker_submission is None:
            raise ValueError("allowed safety assessment requires broker submission.")
        if self.broker_submission is not None and (
            self.broker_submission.symbol != self.assessment.symbol
        ):
            raise ValueError("broker submission symbol must match safety assessment.")

    @property
    def submitted(self) -> bool:
        return self.broker_submission is not None
