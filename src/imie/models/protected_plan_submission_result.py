from __future__ import annotations

from dataclasses import dataclass

from imie.models.protected_order_submission import (
    ProtectedOrderSubmission,
)


@dataclass(frozen=True, slots=True)
class ProtectedPlanSubmissionResult:
    broker: str
    symbol: str
    side: str
    quantity: int
    accepted: bool
    status: str
    message: str
    submissions: tuple[ProtectedOrderSubmission, ...]
    rollback_attempted: bool = False
    rollback_succeeded: bool | None = None
    rolled_back_order_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("broker", "symbol", "side", "status", "message"):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be a string.")

        broker = self.broker.strip().lower()
        symbol = self.symbol.strip().upper()
        side = self.side.strip().lower()
        status = self.status.strip().lower()
        message = self.message.strip()

        if not broker or not symbol or not status or not message:
            raise ValueError("broker, symbol, status, and message cannot be empty.")
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool.")
        if not isinstance(self.submissions, tuple) or not all(
            isinstance(item, ProtectedOrderSubmission)
            for item in self.submissions
        ):
            raise TypeError(
                "submissions must be a tuple of ProtectedOrderSubmission."
            )
        if not self.submissions:
            raise ValueError("submissions cannot be empty.")
        if sum(item.quantity for item in self.submissions) > self.quantity:
            raise ValueError("submitted quantity cannot exceed plan quantity.")
        if self.accepted and (
            sum(item.quantity for item in self.submissions) != self.quantity
            or not all(item.accepted for item in self.submissions)
        ):
            raise ValueError("accepted plan requires every planned slice.")
        if not isinstance(self.rollback_attempted, bool):
            raise TypeError("rollback_attempted must be a bool.")
        if self.rollback_succeeded is not None and not isinstance(
            self.rollback_succeeded,
            bool,
        ):
            raise TypeError("rollback_succeeded must be a bool or None.")
        if not self.rollback_attempted and self.rollback_succeeded is not None:
            raise ValueError("rollback_succeeded requires rollback_attempted.")
        if self.accepted and self.rollback_attempted:
            raise ValueError("an accepted plan cannot have rollback attempts.")

        rolled_back_order_ids = tuple(
            value.strip()
            for value in self.rolled_back_order_ids
            if isinstance(value, str) and value.strip()
        )
        warnings = tuple(
            value.strip()
            for value in self.warnings
            if isinstance(value, str) and value.strip()
        )

        object.__setattr__(self, "broker", broker)
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "rolled_back_order_ids", rolled_back_order_ids)
        object.__setattr__(self, "warnings", warnings)
