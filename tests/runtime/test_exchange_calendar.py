from datetime import date, time

import pytest

from imie.runtime import (
    ExchangeCalendar,
    ExchangeCalendarDay,
)


def test_unconfigured_date_is_normal() -> None:
    calendar = ExchangeCalendar()

    result = calendar.evaluate(
        date(
            2026,
            7,
            20,
        )
    )

    assert result.is_normal_day is True


def test_configured_holiday_is_returned() -> None:
    holiday = ExchangeCalendarDay.holiday(
        calendar_date=date(
            2026,
            7,
            3,
        ),
        name="Independence Day Observed",
    )

    calendar = ExchangeCalendar(
        days=(
            holiday,
        )
    )

    result = calendar.evaluate(
        holiday.calendar_date
    )

    assert result is holiday
    assert calendar.is_holiday(
        holiday.calendar_date
    ) is True


def test_configured_early_close_is_returned() -> None:
    early_close = ExchangeCalendarDay.early_close(
        calendar_date=date(
            2026,
            11,
            27,
        ),
        regular_close=time(
            13,
            0,
        ),
    )

    calendar = ExchangeCalendar(
        days=(
            early_close,
        )
    )

    assert calendar.is_early_close(
        early_close.calendar_date
    ) is True


def test_duplicate_dates_are_rejected() -> None:
    calendar_date = date(
        2026,
        7,
        3,
    )

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        ExchangeCalendar(
            days=(
                ExchangeCalendarDay.holiday(
                    calendar_date=calendar_date,
                    name="First",
                ),
                ExchangeCalendarDay.holiday(
                    calendar_date=calendar_date,
                    name="Second",
                ),
            )
        )


def test_days_must_be_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="tuple",
    ):
        ExchangeCalendar(
            days=[],  # type: ignore[arg-type]
        )


def test_configured_day_count() -> None:
    calendar = ExchangeCalendar(
        days=(
            ExchangeCalendarDay.holiday(
                calendar_date=date(
                    2026,
                    1,
                    1,
                ),
                name="New Year's Day",
            ),
        )
    )

    assert calendar.configured_day_count == 1