from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SessionWakeResult:
    next_allowed_at: datetime | None
    delay_seconds: float | None
    reason: str

    def __post_init__(self) -> None:
        if (
            self.next_allowed_at is not None
            and not isinstance(
                self.next_allowed_at,
                datetime,
            )
        ):
            raise TypeError(
                "next_allowed_at must be a datetime or None."
            )

        if (
            self.next_allowed_at is not None
            and self.next_allowed_at.tzinfo is None
        ):
            raise ValueError(
                "next_allowed_at must be timezone-aware."
            )

        if (
            self.delay_seconds is not None
            and (
                isinstance(
                    self.delay_seconds,
                    bool,
                )
                or not isinstance(
                    self.delay_seconds,
                    int | float,
                )
            )
        ):
            raise TypeError(
                "delay_seconds must be a number or None."
            )

        if (
            self.delay_seconds is not None
            and self.delay_seconds < 0.0
        ):
            raise ValueError(
                "delay_seconds cannot be negative."
            )

        if (
            self.next_allowed_at is None
            and self.delay_seconds is not None
        ):
            raise ValueError(
                "delay_seconds requires next_allowed_at."
            )

        if (
            self.next_allowed_at is not None
            and self.delay_seconds is None
        ):
            raise ValueError(
                "next_allowed_at requires delay_seconds."
            )

        reason = str(
            self.reason
        ).strip()

        if not reason:
            raise ValueError(
                "reason cannot be empty."
            )

        if self.delay_seconds is not None:
            object.__setattr__(
                self,
                "delay_seconds",
                float(
                    self.delay_seconds
                ),
            )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

    @property
    def resolved(self) -> bool:
        return (
            self.next_allowed_at is not None
            and self.delay_seconds is not None
        )