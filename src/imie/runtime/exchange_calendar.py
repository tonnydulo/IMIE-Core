from __future__ import annotations

from datetime import date

from imie.runtime.exchange_calendar_day import (
    ExchangeCalendarDay,
)


class ExchangeCalendar:
    def __init__(
        self,
        days: tuple[ExchangeCalendarDay, ...] = (),
    ) -> None:
        if not isinstance(
            days,
            tuple,
        ):
            raise TypeError(
                "days must be a tuple."
            )

        indexed_days: dict[
            date,
            ExchangeCalendarDay,
        ] = {}

        for day in days:
            if not isinstance(
                day,
                ExchangeCalendarDay,
            ):
                raise TypeError(
                    "days must contain only "
                    "ExchangeCalendarDay values."
                )

            if day.calendar_date in indexed_days:
                raise ValueError(
                    "Exchange calendar dates must be unique."
                )

            indexed_days[
                day.calendar_date
            ] = day

        self._days = indexed_days

    def evaluate(
        self,
        calendar_date: date,
    ) -> ExchangeCalendarDay:
        if not isinstance(
            calendar_date,
            date,
        ):
            raise TypeError(
                "calendar_date must be a date."
            )

        return self._days.get(
            calendar_date,
            ExchangeCalendarDay.normal(
                calendar_date
            ),
        )

    def is_holiday(
        self,
        calendar_date: date,
    ) -> bool:
        return self.evaluate(
            calendar_date
        ).is_holiday

    def is_early_close(
        self,
        calendar_date: date,
    ) -> bool:
        return self.evaluate(
            calendar_date
        ).is_early_close

    @property
    def configured_day_count(self) -> int:
        return len(
            self._days
        )