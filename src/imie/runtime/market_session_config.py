from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class MarketSessionConfig:
    """
    U.S. equity-session boundaries.

    Times are interpreted in market_timezone.
    """

    market_timezone: str = "America/New_York"

    premarket_start: time = time(
        hour=4,
        minute=0,
    )
    regular_start: time = time(
        hour=9,
        minute=30,
    )
    regular_end: time = time(
        hour=16,
        minute=0,
    )
    after_hours_end: time = time(
        hour=20,
        minute=0,
    )

    weekdays: tuple[int, ...] = (
        0,
        1,
        2,
        3,
        4,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.market_timezone,
            str,
        ):
            raise TypeError(
                "market_timezone must be a string."
            )

        normalized_timezone = (
            self.market_timezone.strip()
        )

        if not normalized_timezone:
            raise ValueError(
                "market_timezone cannot be empty."
            )

        try:
            ZoneInfo(
                normalized_timezone
            )
        except Exception as exc:
            raise ValueError(
                "market_timezone must be a valid "
                "IANA timezone."
            ) from exc

        for name in (
            "premarket_start",
            "regular_start",
            "regular_end",
            "after_hours_end",
        ):
            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                time,
            ):
                raise TypeError(
                    f"{name} must be a datetime.time."
                )

        if not (
            self.premarket_start
            < self.regular_start
            < self.regular_end
            < self.after_hours_end
        ):
            raise ValueError(
                "Session boundaries must be ordered as "
                "premarket_start < regular_start < "
                "regular_end < after_hours_end."
            )

        if not isinstance(
            self.weekdays,
            tuple,
        ):
            raise TypeError(
                "weekdays must be a tuple."
            )

        if not self.weekdays:
            raise ValueError(
                "weekdays cannot be empty."
            )

        normalized_weekdays: list[int] = []

        for weekday in self.weekdays:
            if isinstance(
                weekday,
                bool,
            ) or not isinstance(
                weekday,
                int,
            ):
                raise TypeError(
                    "weekdays must contain only integers."
                )

            if not 0 <= weekday <= 6:
                raise ValueError(
                    "weekday values must be between 0 and 6."
                )

            if weekday not in normalized_weekdays:
                normalized_weekdays.append(
                    weekday
                )

        object.__setattr__(
            self,
            "market_timezone",
            normalized_timezone,
        )

        object.__setattr__(
            self,
            "weekdays",
            tuple(
                normalized_weekdays
            ),
        )

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(
            self.market_timezone
        )