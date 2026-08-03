from datetime import date, time

import pytest

from imie.runtime import (
    SUPPORTED_NYSE_CALENDAR_YEARS,
    build_nyse_calendar,
    build_nyse_calendar_2026,
    build_nyse_calendar_2027,
    build_nyse_calendar_2028,
)


def test_supported_years() -> None:
    assert SUPPORTED_NYSE_CALENDAR_YEARS == (
        2026,
        2027,
        2028,
    )


@pytest.mark.parametrize(
    (
        "calendar_date",
        "holiday_name",
    ),
    [
        (
            date(
                2026,
                7,
                3,
            ),
            "Independence Day Observed",
        ),
        (
            date(
                2027,
                7,
                5,
            ),
            "Independence Day Observed",
        ),
        (
            date(
                2028,
                7,
                4,
            ),
            "Independence Day",
        ),
        (
            date(
                2027,
                12,
                24,
            ),
            "Christmas Day Observed",
        ),
    ],
)
def test_multi_year_holidays(
    calendar_date: date,
    holiday_name: str,
) -> None:
    result = build_nyse_calendar().evaluate(
        calendar_date
    )

    assert result.is_holiday is True
    assert result.holiday_name == holiday_name


@pytest.mark.parametrize(
    "calendar_date",
    [
        date(
            2026,
            11,
            27,
        ),
        date(
            2026,
            12,
            24,
        ),
        date(
            2027,
            11,
            26,
        ),
        date(
            2028,
            7,
            3,
        ),
        date(
            2028,
            11,
            24,
        ),
    ],
)
def test_multi_year_early_closes(
    calendar_date: date,
) -> None:
    result = build_nyse_calendar().evaluate(
        calendar_date
    )

    assert result.is_early_close is True
    assert result.regular_close == time(
        13,
        0,
    )
    assert result.after_hours_close == time(
        17,
        0,
    )


def test_2028_new_year_is_not_observed() -> None:
    result = build_nyse_calendar_2028().evaluate(
        date(
            2028,
            1,
            3,
        )
    )

    assert result.is_normal_day is True


def test_single_year_builder_contains_only_requested_year() -> None:
    calendar = build_nyse_calendar(
        2027
    )

    assert calendar.is_holiday(
        date(
            2027,
            1,
            1,
        )
    ) is True

    assert calendar.is_holiday(
        date(
            2026,
            1,
            1,
        )
    ) is False


def test_multiple_selected_years() -> None:
    calendar = build_nyse_calendar(
        2026,
        2028,
    )

    assert calendar.is_holiday(
        date(
            2026,
            1,
            1,
        )
    ) is True

    assert calendar.is_holiday(
        date(
            2028,
            12,
            25,
        )
    ) is True

    assert calendar.is_holiday(
        date(
            2027,
            1,
            1,
        )
    ) is False


def test_duplicate_years_are_deduplicated() -> None:
    calendar = build_nyse_calendar(
        2026,
        2026,
    )

    assert (
        calendar.configured_day_count
        == build_nyse_calendar_2026()
        .configured_day_count
    )


@pytest.mark.parametrize(
    (
        "builder",
        "year",
    ),
    [
        (
            build_nyse_calendar_2026,
            2026,
        ),
        (
            build_nyse_calendar_2027,
            2027,
        ),
        (
            build_nyse_calendar_2028,
            2028,
        ),
    ],
)
def test_year_specific_builders(
    builder,
    year: int,
) -> None:
    calendar = builder()

    assert all(
        calendar.evaluate(
            date(
                year,
                month,
                15,
            )
        ).calendar_date.year
        == year
        for month in range(
            1,
            13,
        )
    )


def test_unsupported_year_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported NYSE calendar year",
    ):
        build_nyse_calendar(
            2029
        )


def test_year_must_be_integer() -> None:
    with pytest.raises(
        TypeError,
        match="integers",
    ):
        build_nyse_calendar(
            "2027",  # type: ignore[arg-type]
        )


def test_default_calendar_contains_all_years() -> None:
    calendar = build_nyse_calendar()

    assert calendar.is_holiday(
        date(
            2026,
            1,
            1,
        )
    ) is True

    assert calendar.is_holiday(
        date(
            2027,
            1,
            1,
        )
    ) is True

    assert calendar.is_holiday(
        date(
            2028,
            12,
            25,
        )
    ) is True