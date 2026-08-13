from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExistingPositionProtectionSubmission:
    label: str
    quantity: int
    accepted: bool
    target_order_id: str | None
    stop_order_id: str | None
    status: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.label, str):
            raise TypeError("label must be a string.")
        label = self.label.strip().lower()
        if label not in {"target1", "target2"}:
            raise ValueError("label must be target1 or target2.")
        object.__setattr__(self, "label", label)
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool.")
        for name in ("target_order_id", "stop_order_id"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be a string or None.")
            normalized = value.strip() if value is not None else None
            object.__setattr__(self, name, normalized or None)
        if self.accepted and (
            self.target_order_id is None or self.stop_order_id is None
        ):
            raise ValueError(
                "accepted protection requires target and stop order IDs."
            )
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
