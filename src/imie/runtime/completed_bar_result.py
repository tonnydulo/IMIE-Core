from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CompletedBarResult:
    """
    Result of evaluating the newest available market bar.

    A result may be rejected because the bar is incomplete,
    duplicated, missing, or improperly timestamped.
    """

    accepted: bool
    is_new: bool
    is_complete: bool

    timestamp: datetime | None

    reason: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.accepted,
            bool,
        ):
            raise TypeError(
                "accepted must be a bool."
            )

        if not isinstance(
            self.is_new,
            bool,
        ):
            raise TypeError(
                "is_new must be a bool."
            )

        if not isinstance(
            self.is_complete,
            bool,
        ):
            raise TypeError(
                "is_complete must be a bool."
            )

        if (
            self.timestamp is not None
            and not isinstance(
                self.timestamp,
                datetime,
            )
        ):
            raise TypeError(
                "timestamp must be a datetime or None."
            )

        reason = str(
            self.reason
        ).strip()

        if not reason:
            raise ValueError(
                "reason cannot be empty."
            )

        object.__setattr__(
            self,
            "reason",
            reason,
        )