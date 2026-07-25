from __future__ import annotations

from typing import Protocol

from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)


class HealthPublisher(Protocol):
    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        ...