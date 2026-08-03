from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)
from typing import Callable

from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)
from imie.runtime.runtime_health_state import (
    RuntimeHealthState,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)
from imie.runtime.health_status_publisher import (
    HealthStatusPublisher,
)
from imie.runtime.health_publisher import (
    HealthPublisher,
)


Clock = Callable[[], datetime]


class RuntimeHealthTracker:
    """
    Tracks the current runtime lifecycle state and preserves
    the transition history for diagnostics and testing.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        publisher: HealthPublisher | None = None,
        status_publisher: HealthStatusPublisher | None = None,
    ) -> None:
        resolved_clock = (
            clock
            or self._utc_now
        )

        if not callable(
            resolved_clock
        ):
            raise TypeError(
                "clock must be callable."
            )

        if status_publisher is not None:
            publish_method = getattr(
                status_publisher,
                "publish",
                None,
            )

            if not callable(
                publish_method
            ):
                raise TypeError(
                    "status_publisher must provide a callable "
                    "publish method."
                )

        if (
            publisher is not None
            and not callable(
                getattr(
                    publisher,
                    "publish",
                    None,
                )
            )
        ):
            
            raise TypeError(
                "publisher must provide publish() or be None."
            )
        
        self.status_publisher = (
            status_publisher
        )

        self._clock = resolved_clock
        self.publisher = publisher

        self._history: list[
            RuntimeHealthSnapshot
        ] = []

        self._last_heartbeat_at: datetime | None = None
        self._last_successful_cycle_at: datetime | None = None
        self._completed_cycle_count = 0

        self.transition(
            RuntimeHealthState.CREATED,
            cycle_count=0,
            message="Runtime health tracker created.",
        )

    @property
    def current(
        self,
    ) -> RuntimeHealthSnapshot:
        return self._history[-1]

    @property
    def history(
        self,
    ) -> tuple[RuntimeHealthSnapshot, ...]:
        return tuple(
            self._history
        )

    def transition(
        self,
        state: RuntimeHealthState,
        *,
        cycle_count: int,
        message: str,
        error: BaseException | None = None,
    ) -> RuntimeHealthSnapshot:
        if not isinstance(
            state,
            RuntimeHealthState,
        ):
            raise TypeError(
                "state must be a RuntimeHealthState."
            )

        self._validate_cycle_count(
            cycle_count
        )

        self._completed_cycle_count = max(
            self._completed_cycle_count,
            cycle_count,
        )

        normalized_message = (
            self._normalize_message(
                message
            )
        )

        if (
            error is not None
            and not isinstance(
                error,
                BaseException,
            )
        ):
            raise TypeError(
                "error must be an exception or None."
            )

        error_type = (
            type(error).__name__
            if error is not None
            else None
        )

        snapshot = RuntimeHealthSnapshot(
            state=state,
            changed_at=self._checked_now(),
            cycle_count=cycle_count,
            message=normalized_message,
            error_type=error_type,
        )

        self._history.append(
            snapshot
        )

        if self.publisher is not None:
            self.publisher.publish(
                snapshot
            )

        self._publish_status(
            checked_at=snapshot.changed_at
        )

        return snapshot

    def heartbeat(
        self,
        *,
        cycle_count: int,
        message: str = "Runtime heartbeat.",
    ) -> RuntimeHealthSnapshot:
        self._validate_cycle_count(
            cycle_count
        )

        normalized_message = (
            self._normalize_message(
                message
            )
        )

        snapshot = RuntimeHealthSnapshot(
            state=self.current.state,
            changed_at=self._checked_now(),
            cycle_count=cycle_count,
            message=normalized_message,
            error_type=None,
        )

        self._last_heartbeat_at = (
            snapshot.changed_at
        )

        if self.publisher is not None:
            self.publisher.publish(
                snapshot
            )

        self._publish_status(
            checked_at=snapshot.changed_at
        )

        return snapshot
    

    @property
    def started_at(
        self,
    ) -> datetime:
        return self._history[0].changed_at


    @property
    def last_heartbeat_at(
        self,
    ) -> datetime | None:
        return self._last_heartbeat_at


    @property
    def last_successful_cycle_at(
        self,
    ) -> datetime | None:
        return self._last_successful_cycle_at

    @staticmethod
    def _validate_cycle_count(
        cycle_count: int,
    ) -> None:
        if isinstance(
            cycle_count,
            bool,
        ) or not isinstance(
            cycle_count,
            int,
        ):
            raise TypeError(
                "cycle_count must be an int."
            )

        if cycle_count < 0:
            raise ValueError(
                "cycle_count cannot be negative."
            )

    @staticmethod
    def _normalize_message(
        message: str,
    ) -> str:
        if not isinstance(
            message,
            str,
        ):
            raise TypeError(
                "message must be a string."
            )

        normalized_message = (
            message.strip()
        )

        if not normalized_message:
            raise ValueError(
                "message cannot be empty."
            )

        return normalized_message

    def _checked_now(
        self,
    ) -> datetime:
        changed_at = self._clock()

        if not isinstance(
            changed_at,
            datetime,
        ):
            raise TypeError(
                "clock must return a datetime."
            )

        if (
            changed_at.tzinfo is None
            or changed_at.utcoffset() is None
        ):
            raise ValueError(
                "clock must return a timezone-aware datetime."
            )

        return changed_at

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(
            timezone.utc
        )
    
    def record_successful_cycle(
        self,
        *,
        cycle_count: int,
    ) -> datetime:
        self._validate_cycle_count(
            cycle_count
        )

        if cycle_count == 0:
            raise ValueError(
                "cycle_count must be greater than zero "
                "for a completed cycle."
            )

        completed_at = self._checked_now()

        self._last_successful_cycle_at = (
            completed_at
        )

        self._completed_cycle_count = (
            cycle_count
        )

        self._publish_status(
            checked_at=completed_at
        )

        return completed_at
    

    def summary(
        self,
        *,
        checked_at: datetime | None = None,
    ) -> RuntimeHealthSummary:
        resolved_checked_at = (
            checked_at
            if checked_at is not None
            else self._checked_now()
        )

        self._validate_aware_datetime(
            field_name="checked_at",
            value=resolved_checked_at,
        )

        started_at = self.started_at

        if resolved_checked_at < started_at:
            raise ValueError(
                "checked_at cannot be before runtime start."
            )

        return RuntimeHealthSummary(
            state=self.current.state,
            started_at=started_at,
            checked_at=resolved_checked_at,
            uptime_seconds=(
                resolved_checked_at
                - started_at
            ).total_seconds(),
            last_transition_at=(
                self.current.changed_at
            ),
            last_heartbeat_at=(
                self._last_heartbeat_at
            ),
            last_successful_cycle_at=(
                self._last_successful_cycle_at
            ),
            completed_cycle_count=(
                self._completed_cycle_count
            ),
            error_type=(
                self.current.error_type
            ),
        )
    

    @staticmethod
    def _validate_aware_datetime(
        *,
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
        
    
    def _publish_status(
        self,
        *,
        checked_at: datetime,
    ) -> None:
        if self.status_publisher is None:
            return

        summary = self.summary(
            checked_at=checked_at
        )

        self.status_publisher.publish(
            summary
        )


    
        