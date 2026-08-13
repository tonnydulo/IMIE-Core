from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.existing_position_protection_result import (
    ExistingPositionProtectionResult,
)
from imie.models.position_protection_attempt_status import (
    PositionProtectionAttemptStatus,
)


@dataclass(frozen=True, slots=True)
class PositionProtectionAttempt:
    attempt_id: str
    broker: str
    symbol: str
    position_updated_at: datetime
    position_fill_ids: tuple[str, ...]
    status: PositionProtectionAttemptStatus
    created_at: datetime
    updated_at: datetime
    message: str
    result: ExistingPositionProtectionResult | None = None

    def __post_init__(self) -> None:
        for name, case in (
            ("attempt_id", None), ("broker", "lower"), ("symbol", "upper")
        ):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(
                self, name, getattr(normalized, case)() if case else normalized
            )
        for name in ("position_updated_at", "created_at", "updated_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot predate created_at.")
        if not isinstance(self.position_fill_ids, tuple) or not all(
            isinstance(item, str) for item in self.position_fill_ids
        ):
            raise TypeError("position_fill_ids must be a tuple of strings.")
        fill_ids = tuple(item.strip() for item in self.position_fill_ids if item.strip())
        if len(set(fill_ids)) != len(fill_ids):
            raise ValueError("position_fill_ids cannot contain duplicates.")
        object.__setattr__(self, "position_fill_ids", fill_ids)
        if not isinstance(self.status, PositionProtectionAttemptStatus):
            raise TypeError("status must be a PositionProtectionAttemptStatus.")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")
        object.__setattr__(self, "message", self.message.strip())
        if self.result is not None and not isinstance(
            self.result, ExistingPositionProtectionResult
        ):
            raise TypeError("result must be ExistingPositionProtectionResult or None.")
        if self.status is PositionProtectionAttemptStatus.RESERVED and self.result:
            raise ValueError("a reserved attempt cannot have a result.")
        if self.status is PositionProtectionAttemptStatus.ACCEPTED and (
            self.result is None or not self.result.accepted
        ):
            raise ValueError("an accepted attempt requires an accepted result.")
        if self.result is not None and (
            self.result.broker != self.broker
            or self.result.symbol != self.symbol
            or self.result.position_updated_at != self.position_updated_at
        ):
            raise ValueError("attempt result identity must match position fingerprint.")

    @property
    def key(self) -> tuple[str, str, datetime, tuple[str, ...]]:
        return self.broker, self.symbol, self.position_updated_at, self.position_fill_ids
