from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from imie.models import MarketBar
from imie.runtime.completed_bar_result import (
    CompletedBarResult,
)


@dataclass(slots=True)
class CompletedBarGuard:
    """
    Accepts only newly completed market bars.

    The guard maintains the timestamp of the last accepted bar so
    repeated polling does not execute the analysis pipeline twice
    for the same completed candle.
    """

    timeframe_minutes: int
    completion_delay_seconds: float = 3.0

    _last_accepted_timestamp: datetime | None = None

    def __post_init__(self) -> None:
        if isinstance(
            self.timeframe_minutes,
            bool,
        ):
            raise TypeError(
                "timeframe_minutes must be an int."
            )

        if not isinstance(
            self.timeframe_minutes,
            int,
        ):
            raise TypeError(
                "timeframe_minutes must be an int."
            )

        if self.timeframe_minutes < 1:
            raise ValueError(
                "timeframe_minutes must be at least 1."
            )

        try:
            delay = float(
                self.completion_delay_seconds
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                "completion_delay_seconds must be numeric."
            ) from exc

        if delay < 0.0:
            raise ValueError(
                "completion_delay_seconds cannot be negative."
            )

        self.completion_delay_seconds = delay

    def evaluate(
        self,
        *,
        bars: list[MarketBar],
        checked_at: datetime | None = None,
    ) -> CompletedBarResult:
        """
        Evaluate the latest returned bar.

        Bar timestamps are interpreted as the opening timestamp of
        each candle. A two-minute candle stamped 14:30 is complete
        after 14:32 plus the configured completion delay.
        """
        now = checked_at or datetime.now(
            timezone.utc
        )

        if not isinstance(
            now,
            datetime,
        ):
            raise TypeError(
                "checked_at must be a datetime or None."
            )

        if now.tzinfo is None:
            raise ValueError(
                "checked_at must be timezone-aware."
            )

        if not isinstance(
            bars,
            list,
        ):
            raise TypeError(
                "bars must be a list."
            )

        if not bars:
            return CompletedBarResult(
                accepted=False,
                is_new=False,
                is_complete=False,
                timestamp=None,
                reason="No market bars are available.",
            )

        latest_bar = bars[-1]

        if not isinstance(
            latest_bar,
            MarketBar,
        ):
            raise TypeError(
                "bars must contain only MarketBar instances."
            )

        timestamp = latest_bar.timestamp

        if not isinstance(
            timestamp,
            datetime,
        ):
            return CompletedBarResult(
                accepted=False,
                is_new=False,
                is_complete=False,
                timestamp=None,
                reason=(
                    "Latest market bar does not have a valid "
                    "datetime timestamp."
                ),
            )

        if timestamp.tzinfo is None:
            return CompletedBarResult(
                accepted=False,
                is_new=False,
                is_complete=False,
                timestamp=timestamp,
                reason=(
                    "Latest market bar timestamp must be "
                    "timezone-aware."
                ),
            )

        completion_time = (
            timestamp
            + timedelta(
                minutes=self.timeframe_minutes,
            )
            + timedelta(
                seconds=self.completion_delay_seconds,
            )
        )

        is_complete = now >= completion_time

        if not is_complete:
            return CompletedBarResult(
                accepted=False,
                is_new=True,
                is_complete=False,
                timestamp=timestamp,
                reason=(
                    "Latest market bar has not completed."
                ),
            )

        is_new = (
            self._last_accepted_timestamp is None
            or timestamp
            > self._last_accepted_timestamp
        )

        if not is_new:
            return CompletedBarResult(
                accepted=False,
                is_new=False,
                is_complete=True,
                timestamp=timestamp,
                reason=(
                    "Latest completed market bar was already "
                    "processed."
                ),
            )

        self._last_accepted_timestamp = timestamp

        return CompletedBarResult(
            accepted=True,
            is_new=True,
            is_complete=True,
            timestamp=timestamp,
            reason=(
                "A new completed market bar is available."
            ),
        )

    @property
    def last_accepted_timestamp(
        self,
    ) -> datetime | None:
        return self._last_accepted_timestamp

    def reset(self) -> None:
        self._last_accepted_timestamp = None