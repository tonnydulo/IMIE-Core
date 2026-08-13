from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.position_protection_reconciliation_result import (
    PositionProtectionReconciliationResult,
)


@dataclass(frozen=True, slots=True)
class PositionProtectionReconciliationRecord:
    result: PositionProtectionReconciliationResult
    position_updated_at: datetime
    position_fill_ids: tuple[str, ...]
    observed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.result, PositionProtectionReconciliationResult):
            raise TypeError(
                "result must be a PositionProtectionReconciliationResult."
            )
        for name in ("position_updated_at", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime):
                raise TypeError(f"{name} must be a datetime.")
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware.")
        if not isinstance(self.position_fill_ids, tuple) or not all(
            isinstance(item, str) for item in self.position_fill_ids
        ):
            raise TypeError("position_fill_ids must be a tuple of strings.")
        fill_ids = tuple(item.strip() for item in self.position_fill_ids if item.strip())
        if len(set(fill_ids)) != len(fill_ids):
            raise ValueError("position_fill_ids cannot contain duplicates.")
        object.__setattr__(self, "position_fill_ids", fill_ids)

    @property
    def position_key(self) -> tuple[str, str, datetime, tuple[str, ...]]:
        return (
            self.result.broker,
            self.result.symbol,
            self.position_updated_at,
            self.position_fill_ids,
        )

    @property
    def key(self) -> tuple[str, str, datetime, tuple[str, ...], datetime]:
        return (*self.position_key, self.observed_at)
