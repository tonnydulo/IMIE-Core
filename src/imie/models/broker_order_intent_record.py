from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.models.execution_order_intent import ExecutionOrderIntent


@dataclass(frozen=True, slots=True)
class BrokerOrderIntentRecord:
    """The exact IMIE intent associated with one submitted broker order."""

    broker: str
    broker_order_id: str
    intent: ExecutionOrderIntent
    recorded_at: datetime
    submission_label: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.broker, str):
            raise TypeError("broker must be a string.")
        broker = self.broker.strip().lower()
        if not broker:
            raise ValueError("broker cannot be empty.")

        if not isinstance(self.broker_order_id, str):
            raise TypeError("broker_order_id must be a string.")
        broker_order_id = self.broker_order_id.strip()
        if not broker_order_id:
            raise ValueError("broker_order_id cannot be empty.")

        if not isinstance(self.intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        if not self.intent.valid or not self.intent.actionable:
            raise ValueError("recorded intent must be valid and actionable.")
        if self.intent.quantity <= 0:
            raise ValueError("recorded intent must have positive quantity.")

        if not isinstance(self.recorded_at, datetime):
            raise TypeError("recorded_at must be a datetime.")
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware.")

        if self.submission_label is not None and not isinstance(
            self.submission_label,
            str,
        ):
            raise TypeError("submission_label must be a string or None.")
        submission_label = (
            self.submission_label.strip().lower()
            if self.submission_label is not None
            else None
        ) or None
        if submission_label not in {None, "entry", "target1", "target2"}:
            raise ValueError(
                "submission_label must be entry, target1, target2, or None."
            )

        object.__setattr__(self, "broker", broker)
        object.__setattr__(self, "broker_order_id", broker_order_id)
        object.__setattr__(self, "submission_label", submission_label)

    @property
    def key(self) -> tuple[str, str]:
        return self.broker, self.broker_order_id

