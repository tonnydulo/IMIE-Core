from __future__ import annotations

from typing import Protocol

from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)


class HealthStatusPublisher(
    Protocol,
):
    def publish(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        ...