from __future__ import annotations

from datetime import date, time

from imie.runtime.exchange_calendar import (
    ExchangeCalendar,
)
from imie.runtime.exchange_calendar_day import (
    ExchangeCalendarDay,
)


SUPPORTED_NYSE_CALENDAR_YEARS: tuple[int, ...] = (
    2026,
    2027,
    2028,
)


def build_nyse_calendar(
    *years: int,
) -> ExchangeCalendar:
    """
    Build an NYSE exchange calendar for one or more supported
    calendar years.

    Supported years reflect the currently published NYSE
    holiday calendar.
    """

    resolved_years = (
        years
        or SUPPORTED_NYSE_CALENDAR_YEARS
    )

    normalized_years = _validate_years(
        resolved_years
    )

    days: list[ExchangeCalendarDay] = []

    for year in normalized_years:
        days.extend(
            _build_year(
                year
            )
        )

    return ExchangeCalendar(
        days=tuple(
            days
        )
    )


def build_nyse_calendar_2026() -> ExchangeCalendar:
    """
    Backward-compatible 2026 NYSE calendar factory.
    """

    return build_nyse_calendar(
        2026
    )


def build_nyse_calendar_2027() -> ExchangeCalendar:
    return build_nyse_calendar(
        2027
    )


def build_nyse_calendar_2028() -> ExchangeCalendar:
    return build_nyse_calendar(
        2028
    )


def _validate_years(
    years: tuple[int, ...],
) -> tuple[int, ...]:
    if not isinstance(
        years,
        tuple,
    ):
        raise TypeError(
            "years must be a tuple."
        )

    if not years:
        raise ValueError(
            "At least one NYSE calendar year is required."
        )

    normalized: list[int] = []

    for year in years:
        if isinstance(
            year,
            bool,
        ) or not isinstance(
            year,
            int,
        ):
            raise TypeError(
                "NYSE calendar years must be integers."
            )

        if (
            year
            not in SUPPORTED_NYSE_CALENDAR_YEARS
        ):
            supported = ", ".join(
                str(value)
                for value
                in SUPPORTED_NYSE_CALENDAR_YEARS
            )

            raise ValueError(
                "Unsupported NYSE calendar year "
                f"{year}. Supported years: {supported}."
            )

        if year not in normalized:
            normalized.append(
                year
            )

    return tuple(
        normalized
    )


def _build_year(
    year: int,
) -> tuple[ExchangeCalendarDay, ...]:
    builders = {
        2026: _build_2026,
        2027: _build_2027,
        2028: _build_2028,
    }

    return builders[
        year
    ]()


def _holiday(
    *,
    year: int,
    month: int,
    day: int,
    name: str,
) -> ExchangeCalendarDay:
    return ExchangeCalendarDay.holiday(
        calendar_date=date(
            year,
            month,
            day,
        ),
        name=name,
    )


def _early_close(
    *,
    year: int,
    month: int,
    day: int,
) -> ExchangeCalendarDay:
    return ExchangeCalendarDay.early_close(
        calendar_date=date(
            year,
            month,
            day,
        ),
        regular_close=time(
            13,
            0,
        ),
        after_hours_close=time(
            17,
            0,
        ),
    )


def _build_2026() -> tuple[
    ExchangeCalendarDay,
    ...,
]:
    return (
        _holiday(
            year=2026,
            month=1,
            day=1,
            name="New Year's Day",
        ),
        _holiday(
            year=2026,
            month=1,
            day=19,
            name="Martin Luther King Jr. Day",
        ),
        _holiday(
            year=2026,
            month=2,
            day=16,
            name="Washington's Birthday",
        ),
        _holiday(
            year=2026,
            month=4,
            day=3,
            name="Good Friday",
        ),
        _holiday(
            year=2026,
            month=5,
            day=25,
            name="Memorial Day",
        ),
        _holiday(
            year=2026,
            month=6,
            day=19,
            name=(
                "Juneteenth National "
                "Independence Day"
            ),
        ),
        _holiday(
            year=2026,
            month=7,
            day=3,
            name="Independence Day Observed",
        ),
        _holiday(
            year=2026,
            month=9,
            day=7,
            name="Labor Day",
        ),
        _holiday(
            year=2026,
            month=11,
            day=26,
            name="Thanksgiving Day",
        ),
        _early_close(
            year=2026,
            month=11,
            day=27,
        ),
        _early_close(
            year=2026,
            month=12,
            day=24,
        ),
        _holiday(
            year=2026,
            month=12,
            day=25,
            name="Christmas Day",
        ),
    )


def _build_2027() -> tuple[
    ExchangeCalendarDay,
    ...,
]:
    return (
        _holiday(
            year=2027,
            month=1,
            day=1,
            name="New Year's Day",
        ),
        _holiday(
            year=2027,
            month=1,
            day=18,
            name="Martin Luther King Jr. Day",
        ),
        _holiday(
            year=2027,
            month=2,
            day=15,
            name="Washington's Birthday",
        ),
        _holiday(
            year=2027,
            month=3,
            day=26,
            name="Good Friday",
        ),
        _holiday(
            year=2027,
            month=5,
            day=31,
            name="Memorial Day",
        ),
        _holiday(
            year=2027,
            month=6,
            day=18,
            name=(
                "Juneteenth National "
                "Independence Day Observed"
            ),
        ),
        _holiday(
            year=2027,
            month=7,
            day=5,
            name="Independence Day Observed",
        ),
        _holiday(
            year=2027,
            month=9,
            day=6,
            name="Labor Day",
        ),
        _holiday(
            year=2027,
            month=11,
            day=25,
            name="Thanksgiving Day",
        ),
        _early_close(
            year=2027,
            month=11,
            day=26,
        ),
        _holiday(
            year=2027,
            month=12,
            day=24,
            name="Christmas Day Observed",
        ),
    )


def _build_2028() -> tuple[
    ExchangeCalendarDay,
    ...,
]:
    return (
        _holiday(
            year=2028,
            month=1,
            day=17,
            name="Martin Luther King Jr. Day",
        ),
        _holiday(
            year=2028,
            month=2,
            day=21,
            name="Washington's Birthday",
        ),
        _holiday(
            year=2028,
            month=4,
            day=14,
            name="Good Friday",
        ),
        _holiday(
            year=2028,
            month=5,
            day=29,
            name="Memorial Day",
        ),
        _holiday(
            year=2028,
            month=6,
            day=19,
            name=(
                "Juneteenth National "
                "Independence Day"
            ),
        ),
        _early_close(
            year=2028,
            month=7,
            day=3,
        ),
        _holiday(
            year=2028,
            month=7,
            day=4,
            name="Independence Day",
        ),
        _holiday(
            year=2028,
            month=9,
            day=4,
            name="Labor Day",
        ),
        _holiday(
            year=2028,
            month=11,
            day=23,
            name="Thanksgiving Day",
        ),
        _early_close(
            year=2028,
            month=11,
            day=24,
        ),
        _holiday(
            year=2028,
            month=12,
            day=25,
            name="Christmas Day",
        ),
    )