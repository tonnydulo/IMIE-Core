from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProtectedOrderSubmission:
    label: str
    quantity: int
    accepted: bool
    broker_order_id: str | None
    status: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.label, str):
            raise TypeError("label must be a string.")
        label = self.label.strip().lower()
        if label not in {"target1", "target2"}:
            raise ValueError("label must be target1 or target2.")

        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool.")

        if self.broker_order_id is not None and not isinstance(
            self.broker_order_id,
            str,
        ):
            raise TypeError("broker_order_id must be a string or None.")
        broker_order_id = (
            self.broker_order_id.strip()
            if self.broker_order_id is not None
            else None
        ) or None

        if self.accepted and broker_order_id is None:
            raise ValueError("an accepted submission requires broker_order_id.")

        if not isinstance(self.status, str):
            raise TypeError("status must be a string.")
        status = self.status.strip().lower()
        if not status:
            raise ValueError("status cannot be empty.")

        if not isinstance(self.message, str):
            raise TypeError("message must be a string.")
        message = self.message.strip()
        if not message:
            raise ValueError("message cannot be empty.")

        object.__setattr__(self, "label", label)
        object.__setattr__(self, "broker_order_id", broker_order_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "message", message)
