from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import ExecutionSubmissionReservation


@runtime_checkable
class ExecutionSubmissionReservationStore(Protocol):
    def reserve(self, reservation: ExecutionSubmissionReservation) -> None:
        ...

    def get(self, fingerprint: str) -> ExecutionSubmissionReservation | None:
        ...
