from datetime import date, time

import pytest

from imie.runtime import (
    ExchangeCalendarDay,
)


CALENDAR_DATE = date(
    2026,
    7,
    20,
)


def test_normal_day() -> None:
    result = ExchangeCalendarDay.normal(
        CALENDAR_DATE
    )

    assert result.is_holiday is False
    assert result.is_early_close is False
    assert result.is_normal_day is True
    assert result.holiday_name is None
    assert result.regular_close is None


def test_holiday() -> None:
    result = ExchangeCalendarDay.holiday(
        calendar_date=CALENDAR_DATE,
        name="Test Holiday",
    )

    assert result.is_holiday is True
    assert result.is_early_close is False
    assert result.is_normal_day is False
    assert result.holiday_name == "Test Holiday"


def test_early_close() -> None:
    result = ExchangeCalendarDay.early_close(
        calendar_date=CALENDAR_DATE,
        regular_close=time(
            13,
            0,
        ),
        after_hours_close=time(
            17,
            0,
        ),
    )

    assert result.is_holiday is False
    assert result.is_early_close is True
    assert result.is_normal_day is False
    assert result.regular_close == time(
        13,
        0,
    )
    assert result.after_hours_close == time(
        17,
        0,
    )


def test_holiday_name_is_trimmed() -> None:
    result = ExchangeCalendarDay.holiday(
        calendar_date=CALENDAR_DATE,
        name=" Test Holiday ",
    )

    assert result.holiday_name == "Test Holiday"


def test_holiday_name_cannot_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="holiday_name",
    ):
        ExchangeCalendarDay.holiday(
            calendar_date=CALENDAR_DATE,
            name=" ",
        )


def test_holiday_cannot_have_close_time() -> None:
    with pytest.raises(
        ValueError,
        match="holiday",
    ):
        ExchangeCalendarDay(
            calendar_date=CALENDAR_DATE,
            is_holiday=True,
            holiday_name="Test Holiday",
            regular_close=time(
                13,
                0,
            ),
        )


def test_regular_close_must_precede_after_hours() -> None:
    with pytest.raises(
        ValueError,
        match="regular_close",
    ):
        ExchangeCalendarDay.early_close(
            calendar_date=CALENDAR_DATE,
            regular_close=time(
                17,
                0,
            ),
            after_hours_close=time(
                13,
                0,
            ),
        )