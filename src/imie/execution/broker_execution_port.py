from __future__ import annotations

from typing import Protocol

from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)


class BrokerExecutionPort(Protocol):
    def submit_order(
        self,
        intent: ExecutionOrderIntent,
    ) -> BrokerSubmissionResult:
        ...