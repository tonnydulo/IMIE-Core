from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.existing_position_protection_result import (
    ExistingPositionProtectionResult,
)


@dataclass(frozen=True, slots=True)
class PositionProtectionRecord:
    result: ExistingPositionProtectionResult
    position_fill_ids: tuple[str, ...]
    recorded_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.result, ExistingPositionProtectionResult):
            raise TypeError("result must be an ExistingPositionProtectionResult.")
        if not self.result.accepted:
            raise ValueError("only accepted position protection can be recorded.")
        if not isinstance(self.position_fill_ids, tuple) or not all(
            isinstance(item, str) for item in self.position_fill_ids
        ):
            raise TypeError("position_fill_ids must be a tuple of strings.")
        fill_ids = tuple(item.strip() for item in self.position_fill_ids if item.strip())
        if len(set(fill_ids)) != len(fill_ids):
            raise ValueError("position_fill_ids cannot contain duplicates.")
        if not isinstance(self.recorded_at, datetime):
            raise TypeError("recorded_at must be a datetime.")
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware.")
        object.__setattr__(self, "position_fill_ids", fill_ids)

    @property
    def key(self) -> tuple[str, str, datetime, tuple[str, ...]]:
        return (
            self.result.broker,
            self.result.symbol,
            self.result.position_updated_at,
            self.position_fill_ids,
        )
