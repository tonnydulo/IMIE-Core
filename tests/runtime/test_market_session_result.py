from datetime import date, datetime, time, timezone

import pytest

from imie.runtime import (
    ExchangeCalendarDay,
    MarketSessionResult,
    MarketSessionState,
)


CHECKED_AT = datetime(
    2026,
    11,
    27,
    17,
    0,
    tzinfo=timezone.utc,
)


def test_result_exposes_early_close() -> None:
    exchange_day = ExchangeCalendarDay.early_close(
        calendar_date=date(
            2026,
            11,
            27,
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

    result = MarketSessionResult(
        state=MarketSessionState.AFTER_HOURS,
        checked_at=CHECKED_AT,
        market_time=CHECKED_AT,
        is_trading_day=True,
        exchange_day=exchange_day,
        reason="Early-close after-hours session.",
    )

    assert result.is_early_close is True
    assert result.is_exchange_holiday is False


def test_result_exposes_exchange_holiday() -> None:
    exchange_day = ExchangeCalendarDay.holiday(
        calendar_date=date(
            2026,
            7,
            3,
        ),
        name="Independence Day Observed",
    )

    result = MarketSessionResult(
        state=MarketSessionState.CLOSED,
        checked_at=CHECKED_AT,
        market_time=CHECKED_AT,
        is_trading_day=False,
        exchange_day=exchange_day,
        reason="Exchange holiday.",
    )

    assert result.is_exchange_holiday is True
    assert result.is_early_close is False


def test_exchange_day_must_be_valid() -> None:
    with pytest.raises(
        TypeError,
        match="ExchangeCalendarDay",
    ):
        MarketSessionResult(
            state=MarketSessionState.CLOSED,
            checked_at=CHECKED_AT,
            market_time=CHECKED_AT,
            is_trading_day=False,
            exchange_day=object(),  # type: ignore[arg-type]
            reason="Invalid exchange day.",
        )