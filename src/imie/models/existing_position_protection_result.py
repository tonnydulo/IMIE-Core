from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.existing_position_protection_submission import (
    ExistingPositionProtectionSubmission,
)


@dataclass(frozen=True, slots=True)
class ExistingPositionProtectionResult:
    broker: str
    symbol: str
    exit_side: str
    position_quantity: int
    requested_quantity: int
    accepted_quantity: int
    position_updated_at: datetime
    accepted: bool
    status: str
    message: str
    submissions: tuple[ExistingPositionProtectionSubmission, ...]
    rollback_attempted: bool = False
    rollback_succeeded: bool | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, case in (("broker", "lower"), ("symbol", "upper")):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(self, name, getattr(normalized, case)())
        if not isinstance(self.exit_side, str):
            raise TypeError("exit_side must be a string.")
        exit_side = self.exit_side.strip().lower()
        if exit_side not in {"buy", "sell"}:
            raise ValueError("exit_side must be buy or sell.")
        object.__setattr__(self, "exit_side", exit_side)
        for name in (
            "position_quantity",
            "requested_quantity",
            "accepted_quantity",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int.")
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")
        if self.requested_quantity > self.position_quantity:
            raise ValueError("requested quantity cannot exceed position quantity.")
        if self.accepted_quantity > self.requested_quantity:
            raise ValueError("accepted quantity cannot exceed requested quantity.")
        if not isinstance(self.position_updated_at, datetime):
            raise TypeError("position_updated_at must be a datetime.")
        if self.position_updated_at.tzinfo is None:
            raise ValueError("position_updated_at must be timezone-aware.")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool.")
        if not isinstance(self.submissions, tuple) or not all(
            isinstance(item, ExistingPositionProtectionSubmission)
            for item in self.submissions
        ):
            raise TypeError(
                "submissions must be ExistingPositionProtectionSubmission items."
            )
        submitted_quantity = sum(item.quantity for item in self.submissions)
        accepted_quantity = sum(
            item.quantity for item in self.submissions if item.accepted
        )
        if submitted_quantity != self.requested_quantity:
            raise ValueError("submission quantities must equal requested quantity.")
        if accepted_quantity != self.accepted_quantity:
            raise ValueError("accepted submission quantity does not match result.")
        if self.accepted and self.accepted_quantity != self.requested_quantity:
            raise ValueError("accepted result requires full requested coverage.")
        if not isinstance(self.rollback_attempted, bool):
            raise TypeError("rollback_attempted must be a bool.")
        if self.rollback_succeeded is not None and not isinstance(
            self.rollback_succeeded, bool
        ):
            raise TypeError("rollback_succeeded must be a bool or None.")
        if not self.rollback_attempted and self.rollback_succeeded is not None:
            raise ValueError("rollback_succeeded requires rollback_attempted.")
        if self.accepted and self.rollback_attempted:
            raise ValueError("accepted result cannot have rollback attempts.")
        for name in ("status", "message"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"{name} cannot be empty.")
            object.__setattr__(
                self, name, normalized.lower() if name == "status" else normalized
            )
        if not isinstance(self.warnings, tuple) or not all(
            isinstance(item, str) for item in self.warnings
        ):
            raise TypeError("warnings must be a tuple of strings.")
        object.__setattr__(
            self,
            "warnings",
            tuple(item.strip() for item in self.warnings if item.strip()),
        )
