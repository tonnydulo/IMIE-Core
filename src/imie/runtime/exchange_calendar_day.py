from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True, slots=True)
class ExchangeCalendarDay:
    calendar_date: date
    is_holiday: bool
    holiday_name: str | None = None
    regular_close: time | None = None
    after_hours_close: time | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.calendar_date,
            date,
        ):
            raise TypeError(
                "calendar_date must be a date."
            )

        if not isinstance(
            self.is_holiday,
            bool,
        ):
            raise TypeError(
                "is_holiday must be a bool."
            )

        holiday_name = self.holiday_name

        if holiday_name is not None:
            if not isinstance(
                holiday_name,
                str,
            ):
                raise TypeError(
                    "holiday_name must be a string or None."
                )

            holiday_name = holiday_name.strip()

            if not holiday_name:
                raise ValueError(
                    "holiday_name cannot be empty."
                )

        for name in (
            "regular_close",
            "after_hours_close",
        ):
            value = getattr(
                self,
                name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    time,
                )
            ):
                raise TypeError(
                    f"{name} must be a time or None."
                )

        if (
            self.is_holiday
            and self.regular_close is not None
        ):
            raise ValueError(
                "A holiday cannot have a regular close."
            )

        if (
            self.is_holiday
            and self.after_hours_close is not None
        ):
            raise ValueError(
                "A holiday cannot have an after-hours close."
            )

        if (
            self.regular_close is not None
            and self.after_hours_close is not None
            and self.regular_close
            >= self.after_hours_close
        ):
            raise ValueError(
                "regular_close must be earlier than "
                "after_hours_close."
            )

        object.__setattr__(
            self,
            "holiday_name",
            holiday_name,
        )

    @property
    def is_early_close(self) -> bool:
        return (
            not self.is_holiday
            and self.regular_close is not None
        )

    @property
    def is_normal_day(self) -> bool:
        return (
            not self.is_holiday
            and not self.is_early_close
        )

    @classmethod
    def normal(
        cls,
        calendar_date: date,
    ) -> ExchangeCalendarDay:
        return cls(
            calendar_date=calendar_date,
            is_holiday=False,
        )

    @classmethod
    def holiday(
        cls,
        *,
        calendar_date: date,
        name: str,
    ) -> ExchangeCalendarDay:
        return cls(
            calendar_date=calendar_date,
            is_holiday=True,
            holiday_name=name,
        )

    @classmethod
    def early_close(
        cls,
        *,
        calendar_date: date,
        regular_close: time,
        after_hours_close: time | None = None,
    ) -> ExchangeCalendarDay:
        return cls(
            calendar_date=calendar_date,
            is_holiday=False,
            regular_close=regular_close,
            after_hours_close=after_hours_close,
        )