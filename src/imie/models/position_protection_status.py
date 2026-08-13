from __future__ import annotations

from dataclasses import dataclass

from imie.models.execution_position import ExecutionPosition
from imie.models.position_protection_attempt import PositionProtectionAttempt
from imie.models.position_protection_record import PositionProtectionRecord


@dataclass(frozen=True, slots=True)
class PositionProtectionStatus:
    broker: str
    symbol: str
    state: str
    position: ExecutionPosition | None
    attempt: PositionProtectionAttempt | None
    record: PositionProtectionRecord | None

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
            object.__setattr__(self, name, getattr(value.strip(), case)())
        if self.state not in {
            "no_position",
            "flat",
            "unprotected",
            "reserved",
            "accepted",
            "failed",
            "uncertain",
        }:
            raise ValueError("state is not a supported protection state.")
        if self.position is not None and not isinstance(
            self.position, ExecutionPosition
        ):
            raise TypeError("position must be ExecutionPosition or None.")
        if self.attempt is not None and not isinstance(
            self.attempt, PositionProtectionAttempt
        ):
            raise TypeError("attempt must be PositionProtectionAttempt or None.")
        if self.record is not None and not isinstance(
            self.record, PositionProtectionRecord
        ):
            raise TypeError("record must be PositionProtectionRecord or None.")
