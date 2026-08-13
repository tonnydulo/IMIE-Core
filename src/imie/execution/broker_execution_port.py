from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import (
    BrokerSubmissionResult,
    ExecutionOrderIntent,
)


@runtime_checkable
class BrokerExecutionPort(Protocol):
    def submit_order(
        self,
        intent: ExecutionOrderIntent,
    ) -> BrokerSubmissionResult:
        ...
