from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from imie.runtime.runtime_health_state import (
    RuntimeHealthState,
)


@dataclass(frozen=True, slots=True)
class RuntimeHealthSnapshot:
    state: RuntimeHealthState
    changed_at: datetime
    cycle_count: int
    message: str
    error_type: str | None = None

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.state,
            RuntimeHealthState,
        ):
            raise TypeError(
                "state must be a RuntimeHealthState."
            )

        if not isinstance(
            self.changed_at,
            datetime,
        ):
            raise TypeError(
                "changed_at must be a datetime."
            )

        if self.changed_at.tzinfo is None:
            raise ValueError(
                "changed_at must be timezone-aware."
            )

        if isinstance(
            self.cycle_count,
            bool,
        ) or not isinstance(
            self.cycle_count,
            int,
        ):
            raise TypeError(
                "cycle_count must be an int."
            )

        if self.cycle_count < 0:
            raise ValueError(
                "cycle_count cannot be negative."
            )

        message = str(
            self.message
        ).strip()

        if not message:
            raise ValueError(
                "message cannot be empty."
            )

        if (
            self.error_type is not None
            and not isinstance(
                self.error_type,
                str,
            )
        ):
            raise TypeError(
                "error_type must be a string or None."
            )

        normalized_error_type = (
            self.error_type.strip()
            if self.error_type is not None
            else None
        )

        if normalized_error_type == "":
            normalized_error_type = None

        object.__setattr__(
            self,
            "message",
            message,
        )

        object.__setattr__(
            self,
            "error_type",
            normalized_error_type,
        )

    @property
    def failed(
        self,
    ) -> bool:
        return (
            self.state
            is RuntimeHealthState.FAILED
        )

    @property
    def terminal(
        self,
    ) -> bool:
        return self.state in {
            RuntimeHealthState.STOPPED,
            RuntimeHealthState.FAILED,
        }