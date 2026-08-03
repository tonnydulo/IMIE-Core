from __future__ import annotations

from threading import Event


class InterruptibleSleeper:
    """
    Provides an event-backed wait that can be interrupted by a
    runtime shutdown request.
    """

    def __init__(
        self,
    ) -> None:
        self._interrupt_event = Event()

    @property
    def interrupted(
        self,
    ) -> bool:
        return self._interrupt_event.is_set()

    def wait(
        self,
        seconds: float,
    ) -> bool:
        """
        Wait for the requested duration.

        Returns True when interrupted before the timeout expires.
        Returns False when the full timeout expires normally.
        """

        resolved_seconds = self._validate_seconds(
            seconds
        )

        return self._interrupt_event.wait(
            timeout=resolved_seconds
        )

    def interrupt(
        self,
    ) -> None:
        self._interrupt_event.set()

    def reset(
        self,
    ) -> None:
        self._interrupt_event.clear()

    @staticmethod
    def _validate_seconds(
        seconds: float,
    ) -> float:
        if isinstance(
            seconds,
            bool,
        ) or not isinstance(
            seconds,
            int | float,
        ):
            raise TypeError(
                "seconds must be a number."
            )

        resolved_seconds = float(
            seconds
        )

        if resolved_seconds < 0.0:
            raise ValueError(
                "seconds cannot be negative."
            )

        return resolved_seconds