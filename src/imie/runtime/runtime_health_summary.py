from __future__ import annotations

import json

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from imie.runtime.runtime_health_state import (
    RuntimeHealthState,
)


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeHealthSummary:
    state: RuntimeHealthState
    started_at: datetime
    checked_at: datetime
    uptime_seconds: float
    last_transition_at: datetime
    last_heartbeat_at: datetime | None
    last_successful_cycle_at: datetime | None
    completed_cycle_count: int
    error_type: str | None

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

        for field_name in (
            "started_at",
            "checked_at",
            "last_transition_at",
        ):
            value = getattr(
                self,
                field_name,
            )

            self._validate_aware_datetime(
                field_name,
                value,
            )

        for field_name in (
            "last_heartbeat_at",
            "last_successful_cycle_at",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                self._validate_aware_datetime(
                    field_name,
                    value,
                )

        if isinstance(
            self.uptime_seconds,
            bool,
        ) or not isinstance(
            self.uptime_seconds,
            int | float,
        ):
            raise TypeError(
                "uptime_seconds must be a number."
            )

        if self.uptime_seconds < 0:
            raise ValueError(
                "uptime_seconds cannot be negative."
            )

        object.__setattr__(
            self,
            "uptime_seconds",
            float(
                self.uptime_seconds
            ),
        )

        if isinstance(
            self.completed_cycle_count,
            bool,
        ) or not isinstance(
            self.completed_cycle_count,
            int,
        ):
            raise TypeError(
                "completed_cycle_count must be an int."
            )

        if self.completed_cycle_count < 0:
            raise ValueError(
                "completed_cycle_count cannot be negative."
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

        if self.checked_at < self.started_at:
            raise ValueError(
                "checked_at cannot be before started_at."
            )

        if (
            self.last_transition_at
            < self.started_at
        ):
            raise ValueError(
                "last_transition_at cannot be before "
                "started_at."
            )

    @property
    def running(
        self,
    ) -> bool:
        return self.state in {
            RuntimeHealthState.STARTING,
            RuntimeHealthState.CONNECTED,
            RuntimeHealthState.RUNNING,
            RuntimeHealthState.SLEEPING,
            RuntimeHealthState.STOPPING,
        }

    @property
    def terminal(
        self,
    ) -> bool:
        return self.state in {
            RuntimeHealthState.STOPPED,
            RuntimeHealthState.FAILED,
        }

    @property
    def failed(
        self,
    ) -> bool:
        return (
            self.state
            is RuntimeHealthState.FAILED
        )

    @staticmethod
    def _validate_aware_datetime(
        field_name: str,
        value: object,
    ) -> None:
        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                f"{field_name} must be a datetime."
            )

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                f"{field_name} must be timezone-aware."
            )
        
    @property
    def health_summary(
        self,
    ) -> RuntimeHealthSummary:
        return (
            self.continuous_runner
            .health_tracker
            .summary()
        )
    
    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "started_at": self.started_at.isoformat(),
            "checked_at": self.checked_at.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "last_transition_at": (
                self.last_transition_at.isoformat()
            ),
            "last_heartbeat_at": (
                self.last_heartbeat_at.isoformat()
                if self.last_heartbeat_at is not None
                else None
            ),
            "last_successful_cycle_at": (
                self.last_successful_cycle_at.isoformat()
                if (
                    self.last_successful_cycle_at
                    is not None
                )
                else None
            ),
            "completed_cycle_count": (
                self.completed_cycle_count
            ),
            "error_type": self.error_type,
            "running": self.running,
            "terminal": self.terminal,
            "failed": self.failed,
        }
  

    def to_json(
        self,
        *,
        indent: int | None = None,
    ) -> str:
        if (
            indent is not None
            and (
                isinstance(
                    indent,
                    bool,
                )
                or not isinstance(
                    indent,
                    int,
                )
            )
        ):
            raise TypeError(
                "indent must be an int or None."
            )

        if (
            indent is not None
            and indent < 0
        ):
            raise ValueError(
                "indent cannot be negative."
            )

        if indent is None:
            return json.dumps(
                self.to_dict(),
                separators=(
                    ",",
                    ":",
                ),
                sort_keys=True,
            )

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
        )