from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from imie.runtime import (
    MarketSessionClock,
    MarketSessionState,
    build_nyse_calendar_2026,
)


NEW_YORK = ZoneInfo(
    "America/New_York"
)


def eastern_time(
    *,
    year: int = 2026,
    month: int = 7,
    day: int = 20,
    hour: int,
    minute: int = 0,
) -> datetime:
    return datetime(
        year,
        month,
        day,
        hour,
        minute,
        tzinfo=NEW_YORK,
    )


@pytest.mark.parametrize(
    (
        "checked_at",
        "expected_state",
    ),
    [
        (
            eastern_time(
                hour=3,
                minute=59,
            ),
            MarketSessionState.CLOSED,
        ),
        (
            eastern_time(
                hour=4,
            ),
            MarketSessionState.PREMARKET,
        ),
        (
            eastern_time(
                hour=9,
                minute=29,
            ),
            MarketSessionState.PREMARKET,
        ),
        (
            eastern_time(
                hour=9,
                minute=30,
            ),
            MarketSessionState.REGULAR_SESSION,
        ),
        (
            eastern_time(
                hour=15,
                minute=59,
            ),
            MarketSessionState.REGULAR_SESSION,
        ),
        (
            eastern_time(
                hour=16,
            ),
            MarketSessionState.AFTER_HOURS,
        ),
        (
            eastern_time(
                hour=19,
                minute=59,
            ),
            MarketSessionState.AFTER_HOURS,
        ),
        (
            eastern_time(
                hour=20,
            ),
            MarketSessionState.CLOSED,
        ),
    ],
)
def test_session_boundaries(
    checked_at: datetime,
    expected_state: MarketSessionState,
) -> None:
    result = MarketSessionClock().evaluate(
        checked_at
    )

    assert result.state is expected_state


def test_weekend_is_closed() -> None:
    result = MarketSessionClock().evaluate(
        eastern_time(
            day=18,
            hour=10,
        )
    )

    assert (
        result.state
        is MarketSessionState.CLOSED
    )
    assert result.is_trading_day is False
    assert result.is_open_session is False


def test_regular_session_properties() -> None:
    result = MarketSessionClock().evaluate(
        eastern_time(
            hour=10,
        )
    )

    assert (
        result.state
        is MarketSessionState.REGULAR_SESSION
    )
    assert result.is_trading_day is True
    assert result.is_open_session is True
    assert result.is_regular_session is True


def test_utc_time_is_converted_to_market_time() -> None:
    checked_at = datetime(
        2026,
        7,
        20,
        14,
        0,
        tzinfo=timezone.utc,
    )

    result = MarketSessionClock().evaluate(
        checked_at
    )

    assert result.market_time.hour == 10
    assert (
        result.market_time.tzinfo
        == NEW_YORK
    )
    assert (
        result.state
        is MarketSessionState.REGULAR_SESSION
    )


def test_checked_at_must_be_timezone_aware() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        MarketSessionClock().evaluate(
            datetime(
                2026,
                7,
                20,
                10,
                0,
            )
        )


def test_checked_at_must_be_datetime_or_none() -> None:
    with pytest.raises(
        TypeError,
        match="datetime or None",
    ):
        MarketSessionClock().evaluate(
            "2026-07-20",  # type: ignore[arg-type]
        )

def test_nyse_holiday_is_closed() -> None:
    clock = MarketSessionClock(
        exchange_calendar=(
            build_nyse_calendar_2026()
        )
    )

    result = clock.evaluate(
        eastern_time(
            month=7,
            day=3,
            hour=10,
        )
    )

    assert (
        result.state
        is MarketSessionState.CLOSED
    )
    assert result.is_trading_day is False
    assert result.is_exchange_holiday is True
    assert result.exchange_day is not None
    assert (
        result.exchange_day.holiday_name
        == "Independence Day Observed"
    )
    assert (
        "Independence Day Observed"
        in result.reason
    )


def test_early_close_before_one_is_regular() -> None:
    clock = MarketSessionClock(
        exchange_calendar=(
            build_nyse_calendar_2026()
        )
    )

    result = clock.evaluate(
        eastern_time(
            month=11,
            day=27,
            hour=12,
            minute=59,
        )
    )

    assert (
        result.state
        is MarketSessionState.REGULAR_SESSION
    )
    assert result.is_early_close is True


def test_early_close_at_one_is_after_hours() -> None:
    clock = MarketSessionClock(
        exchange_calendar=(
            build_nyse_calendar_2026()
        )
    )

    result = clock.evaluate(
        eastern_time(
            month=11,
            day=27,
            hour=13,
        )
    )

    assert (
        result.state
        is MarketSessionState.AFTER_HOURS
    )
    assert result.is_early_close is True


def test_early_close_before_five_is_after_hours() -> None:
    clock = MarketSessionClock(
        exchange_calendar=(
            build_nyse_calendar_2026()
        )
    )

    result = clock.evaluate(
        eastern_time(
            month=11,
            day=27,
            hour=16,
            minute=59,
        )
    )

    assert (
        result.state
        is MarketSessionState.AFTER_HOURS
    )


def test_early_close_at_five_is_closed() -> None:
    clock = MarketSessionClock(
        exchange_calendar=(
            build_nyse_calendar_2026()
        )
    )

    result = clock.evaluate(
        eastern_time(
            month=11,
            day=27,
            hour=17,
        )
    )

    assert (
        result.state
        is MarketSessionState.CLOSED
    )
    assert result.is_trading_day is True
    assert result.is_early_close is True


def test_exchange_calendar_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="ExchangeCalendar",
    ):
        MarketSessionClock(
            exchange_calendar=object(),  # type: ignore[arg-type]
        )

